import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from dataclasses import dataclass
from time import perf_counter
from pathlib import Path
from .engine import GAConfig, GASimulation

DEFAULT_DB_PATH= Path(__file__).resolve().parents[2]/"results"/"ga_results.db"

SCHEMA= """
CREATE TABLE IF NOT EXISTS runs(
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    function TEXT NOT NULL,
    goal TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    scope_min REAL NOT NULL,
    scope_max REAL NOT NULL,
    precision REAL NOT NULL,
    population INTEGER NOT NULL,
    epochs INTEGER NOT NULL,
    selection_method TEXT NOT NULL,
    selection_count INTEGER,
    tournament_size INTEGER,
    elitism_rate REAL,
    chromosome_mode TEXT NOT NULL,
    crossover_method TEXT NOT NULL,
    crossover_rate REAL NOT NULL,
    mutation_method TEXT NOT NULL,
    mutation_rate REAL NOT NULL,
    inversion_rate REAL,
    seed INTEGER,
    bit_len INTEGER NOT NULL,
    elite_count INTEGER NOT NULL,
    config_json TEXT NOT NULL,
    -- pure algorithm time (population init + all epochs), without the time spent writing to this db
    compute_time_s REAL,
    best_fitness REAL,
    best_epoch INTEGER,
    best_x TEXT
);

CREATE TABLE IF NOT EXISTS epoch_stats(
    run_id INTEGER NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    epoch INTEGER NOT NULL,
    best_fitness REAL NOT NULL,
    mean_fitness REAL NOT NULL,
    worst_fitness REAL NOT NULL,
    std_fitness REAL NOT NULL,
    best_x TEXT NOT NULL,
    u_genotype INTEGER NOT NULL,
    PRIMARY KEY(run_id, epoch)
);

CREATE TABLE IF NOT EXISTS individuals(
    run_id INTEGER NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
    epoch INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    fitness REAL,
    x TEXT NOT NULL,
    genotype TEXT NOT NULL,
    PRIMARY KEY(run_id, epoch, idx)
);

-- repeated runs of the same configuration grouped together (config_json is identical when the seed is not set)
CREATE VIEW IF NOT EXISTS config_summary AS
SELECT config_json, function, goal, dimensions, population, epochs, selection_method, crossover_method, crossover_rate,
       mutation_method, mutation_rate, inversion_rate, elitism_rate, chromosome_mode,
       COUNT(*) AS runs,
       AVG(best_fitness) AS mean_best,
       CASE goal WHEN 'min' THEN MIN(best_fitness) ELSE MAX(best_fitness) END AS best_of_runs,
       CASE goal WHEN 'min' THEN MAX(best_fitness) ELSE MIN(best_fitness) END AS worst_of_runs,
       AVG(compute_time_s) AS mean_time_s,
       MIN(compute_time_s) AS min_time_s,
       MAX(compute_time_s) AS max_time_s,
       GROUP_CONCAT(run_id) AS run_ids
FROM runs
WHERE finished_at IS NOT NULL
GROUP BY config_json;
"""

# columns added after the first version of the schema - added to older databases on open
LATE_RUN_COLUMNS= {"compute_time_s": "REAL", "best_fitness": "REAL", "best_epoch": "INTEGER", "best_x": "TEXT"}


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class SQLiteRecorder:
    """Dumps a GASimulation to SQLite: run config, per-epoch stats and optionally every individual of every epoch.
    A whole run is a single transaction - committed in finish_run, so an interrupted run leaves nothing behind."""

    def __init__(self, db_path: str | Path= DEFAULT_DB_PATH, save_individuals: bool= False):
        self.db_path= Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn= sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._migrate()
        self.conn.executescript(SCHEMA)
        self.save_individuals= save_individuals
        self.run_id: int | None= None
        # time spent on db writes, so it can be subtracted from the measured run time
        self.write_time= 0.0

    def _migrate(self):
        existing= {row[1] for row in self.conn.execute("PRAGMA table_info(runs)")}
        if not existing: return
        for name, sql_type in LATE_RUN_COLUMNS.items():
            if name not in existing: self.conn.execute(f"ALTER TABLE runs ADD COLUMN {name} {sql_type}")

    def start_run(self, sim: GASimulation) -> int:
        cfg= sim.config
        cur= self.conn.execute(
            """INSERT INTO runs(started_at, function, goal, dimensions, scope_min, scope_max, precision, population, epochs,
                selection_method, selection_count, tournament_size, elitism_rate, chromosome_mode, crossover_method,
                crossover_rate, mutation_method, mutation_rate, inversion_rate, seed, bit_len, elite_count, config_json)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (_now(), cfg.function, cfg.goal, cfg.dimensions, cfg.scope[0], cfg.scope[1], cfg.precision, cfg.population,
             cfg.epochs, cfg.selection_method, cfg.selection_count, cfg.tournament_size, cfg.elitism_rate,
             cfg.chromosome_mode, cfg.crossover_method, cfg.crossover_rate, cfg.mutation_method, cfg.mutation_rate,
             cfg.inversion_rate, cfg.seed, sim.bit_len, sim.elite_count, json.dumps(asdict(cfg))),
        )
        self.run_id= cur.lastrowid
        # the initial population (epoch 0) is already evaluated in GASimulation.__init__
        self.log_epoch(sim)
        return self.run_id

    def log_epoch(self, sim: GASimulation):
        if self.run_id is None: raise RuntimeError("start_run must be called before log_epoch.")
        start= perf_counter()
        stats= sim.history[-1]
        self.conn.execute(
            "INSERT INTO epoch_stats VALUES(?,?,?,?,?,?,?,?)",
            (self.run_id, stats.epoch, stats.best_fitness, stats.mean_fitness, stats.worst_fitness, stats.std_fitness,
             json.dumps(stats.best_x), stats.u_genotype),
        )
        if self.save_individuals:
            self.conn.executemany(
                "INSERT INTO individuals VALUES(?,?,?,?,?,?)",
                ((self.run_id, sim.epoch, i, ind.fitness_score, json.dumps(sim.decode(ind)),
                  json.dumps(["".join(map(str, ch)) for ch in ind.chromosomes]))
                 for i, ind in enumerate(sim.population)),
            )
        self.write_time+= perf_counter()-start

    def finish_run(self, sim: GASimulation, compute_time: float):
        best= best_epoch(sim)
        self.conn.execute(
            "UPDATE runs SET finished_at=?, compute_time_s=?, best_fitness=?, best_epoch=?, best_x=? WHERE run_id=?",
            (_now(), compute_time, best.best_fitness, best.epoch, json.dumps(best.best_x), self.run_id),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


def best_epoch(sim: GASimulation):
    pick= min if sim.config.goal=="min" else max
    return pick(sim.history, key=lambda stat: stat.best_fitness)


@dataclass
class RecordedRun:
    sim: GASimulation
    run_id: int
    compute_time: float


def run_with_recording(config: GAConfig, db_path: str | Path= DEFAULT_DB_PATH, save_individuals: bool= False) -> RecordedRun:
    """Builds and runs the simulation, recording it. compute_time covers creating the initial population and all
    epochs, without the time spent writing to the database."""
    recorder= SQLiteRecorder(db_path, save_individuals)
    try:
        start= perf_counter()
        sim= GASimulation(config)
        init_time= perf_counter()-start
        run_id= recorder.start_run(sim)

        recorder.write_time= 0.0
        start= perf_counter()
        sim.run(on_epoch=lambda _: recorder.log_epoch(sim))
        compute_time= init_time+perf_counter()-start-recorder.write_time

        recorder.finish_run(sim, compute_time)
        return RecordedRun(sim, run_id, compute_time)
    finally:
        recorder.close()
