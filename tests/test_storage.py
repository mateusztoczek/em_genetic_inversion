import json
import sqlite3

import pytest

from src.core.storage import SQLiteRecorder, run_with_recording
from tests.test_engine import make_config


def test_run_with_recording_dumps_everything(tmp_path):
    db= tmp_path/"ga.db"
    rec= run_with_recording(make_config(population=10, epochs=4), db, save_individuals=True)
    sim, run_id= rec.sim, rec.run_id

    conn= sqlite3.connect(db)
    run= conn.execute("SELECT function, population, epochs, finished_at, compute_time_s, best_fitness, best_x FROM runs WHERE run_id=?", (run_id,)).fetchone()
    assert run[:3]==("mccormick", 10, 4)
    assert run[3] is not None
    assert run[4]==rec.compute_time and run[4]> 0
    assert run[5]==min(stat.best_fitness for stat in sim.history)
    assert len(json.loads(run[6]))==2

    epochs= conn.execute("SELECT epoch, best_fitness, u_genotype FROM epoch_stats WHERE run_id=? ORDER BY epoch", (run_id,)).fetchall()
    assert [e[0] for e in epochs]==list(range(5))
    assert [e[1] for e in epochs]==[stat.best_fitness for stat in sim.history]

    counts= conn.execute("SELECT epoch, COUNT(*) FROM individuals WHERE run_id=? GROUP BY epoch", (run_id,)).fetchall()
    assert counts==[(e, 10) for e in range(5)]

    x, genotype= conn.execute("SELECT x, genotype FROM individuals WHERE run_id=? AND epoch=4 AND idx=0", (run_id,)).fetchone()
    assert len(json.loads(x))==2
    assert json.loads(genotype)==["".join(map(str, ch)) for ch in sim.population.population[0].chromosomes]
    conn.close()


def test_runs_append_to_same_db(tmp_path):
    db= tmp_path/"ga.db"
    first= run_with_recording(make_config(epochs=2), db).run_id
    second= run_with_recording(make_config(epochs=2), db).run_id
    assert second==first+1


def test_individuals_not_saved_by_default(tmp_path):
    db= tmp_path/"ga.db"
    run_with_recording(make_config(epochs=2), db)
    conn= sqlite3.connect(db)
    assert conn.execute("SELECT COUNT(*) FROM individuals").fetchone()==(0,)
    assert conn.execute("SELECT COUNT(*) FROM epoch_stats").fetchone()==(3,)
    conn.close()


def test_config_summary_groups_repeated_runs(tmp_path):
    db= tmp_path/"ga.db"
    results= [run_with_recording(make_config(goal="max", epochs=3, seed=None), db) for _ in range(3)]
    run_with_recording(make_config(epochs=3, seed=None, population=10), db)
    bests= [max(stat.best_fitness for stat in r.sim.history) for r in results]

    conn= sqlite3.connect(db)
    row= conn.execute("SELECT runs, mean_best, best_of_runs, worst_of_runs, mean_time_s FROM config_summary WHERE goal='max'").fetchone()
    assert row[0]==3
    assert row[1]==pytest.approx(sum(bests)/3)
    assert (row[2], row[3])==(max(bests), min(bests))
    assert row[4]==pytest.approx(sum(r.compute_time for r in results)/3)
    assert conn.execute("SELECT COUNT(*) FROM config_summary").fetchone()==(2,)
    conn.close()


def test_old_database_gets_new_columns(tmp_path):
    db= tmp_path/"ga.db"
    conn= sqlite3.connect(db)
    conn.execute("CREATE TABLE runs(run_id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT)")
    conn.close()
    SQLiteRecorder(db).close()
    conn= sqlite3.connect(db)
    columns= {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
    assert {"compute_time_s", "best_fitness", "best_epoch", "best_x"}<= columns
    conn.close()
