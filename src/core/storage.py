import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from .engine import GASimulation

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
    config_json TEXT NOT NULL
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
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class SQLiteRecorder:
    """Dumps a GASimulation to SQLite: run config, per-epoch stats and every individual of every epoch.
    A whole run is a single transaction - committed in finish_run, so an interrupted run leaves nothing behind."""

    def __init__(self, db_path: str | Path= DEFAULT_DB_PATH):
        self.db_path= Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn= sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.run_id: int | None= None

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
        stats= sim.history[-1]
        self.conn.execute(
            "INSERT INTO epoch_stats VALUES(?,?,?,?,?,?,?,?)",
            (self.run_id, stats.epoch, stats.best_fitness, stats.mean_fitness, stats.worst_fitness, stats.std_fitness,
             json.dumps(stats.best_x), stats.u_genotype),
        )
        self.conn.executemany(
            "INSERT INTO individuals VALUES(?,?,?,?,?,?)",
            ((self.run_id, sim.epoch, i, ind.fitness_score, json.dumps(sim.decode(ind)),
              json.dumps(["".join(map(str, ch)) for ch in ind.chromosomes]))
             for i, ind in enumerate(sim.population)),
        )

    def finish_run(self):
        self.conn.execute("UPDATE runs SET finished_at=? WHERE run_id=?", (_now(), self.run_id))
        self.conn.commit()

    def close(self):
        self.conn.close()


def run_with_recording(sim: GASimulation, db_path: str | Path= DEFAULT_DB_PATH) -> int:
    recorder= SQLiteRecorder(db_path)
    try:
        run_id= recorder.start_run(sim)
        sim.run(on_epoch=lambda _: recorder.log_epoch(sim))
        recorder.finish_run()
        return run_id
    finally:
        recorder.close()
