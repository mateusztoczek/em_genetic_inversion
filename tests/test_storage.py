import json
import sqlite3

from src.core.engine import GASimulation
from src.core.storage import run_with_recording
from tests.test_engine import make_config


def test_run_with_recording_dumps_everything(tmp_path):
    db= tmp_path/"ga.db"
    sim= GASimulation(make_config(population=10, epochs=4))
    run_id= run_with_recording(sim, db)

    conn= sqlite3.connect(db)
    run= conn.execute("SELECT function, population, epochs, finished_at FROM runs WHERE run_id=?", (run_id,)).fetchone()
    assert run[:3]==("mccormick", 10, 4)
    assert run[3] is not None

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
    first= run_with_recording(GASimulation(make_config(epochs=2)), db)
    second= run_with_recording(GASimulation(make_config(epochs=2)), db)
    assert second==first+1
