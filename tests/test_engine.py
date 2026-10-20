import pytest
import math

from src.core.engine import evaluate_individual, decode_individual, GAConfig, GASimulation
from src.core.ga_structure import GAIndividual
from src.core.functions import get_function


def test_evaluate_individual():
    ind= GAIndividual(
        chromosomes=[
            [0,0,0,0],
            [1,1,1,1]
        ]
    )

    def f_func(x):
        return x[0]**2+x[1]**2

    evaluate_individual(ind, f_func, -2.0, 2.0)
    assert ind.fitness_score==pytest.approx(8.0)


def make_config(**overrides) -> GAConfig:
    params= dict(
        function="mccormick",
        goal="min",
        dimensions=2,
        scope=(-3.0, 4.0),
        precision=0.0001,
        population=20,
        epochs=5,
        selection_method="tournament",
        seed=1,
    )
    params.update(overrides)
    return GAConfig(**params)


def test_initial_population():
    sim= GASimulation(make_config())
    res_func= get_function("mccormick",2)
    assert len(sim.population.population)==20
    assert sim.epoch==0
    assert len(sim.history)==1

    for ind in sim.population:
        assert len(ind.chromosomes)==2
        assert ind.fitness_score is not None
        assert math.isfinite(ind.fitness_score)

        x= decode_individual(ind, -3.0,4.0)

        assert all(-3.0 <=xi <=4.0 for xi in x)
        assert ind.fitness_score== pytest.approx(res_func(x))


@pytest.mark.parametrize("method,count", [("best", 5), ("worst", 5), ("natural", None), ("tournament", None), ("roulette", None)])
def test_run_all_selections(method, count):
    sim= GASimulation(make_config(selection_method=method, selection_count=count, elitism_rate=0.2))
    seen= []
    history= sim.run(on_epoch=seen.append)

    assert sim.finished
    assert len(history)==6
    assert [s.epoch for s in seen]==[1,2,3,4,5]
    assert len(sim.population.population)==20


def test_elitism_keeps_best():
    sim= GASimulation(make_config(selection_method="worst", selection_count=5, elitism_rate=0.1))
    history= sim.run()
    # elite copies the best individual every epoch, so best fitness can never get worse
    bests= [s.best_fitness for s in history]
    assert all(b2<= b1 for b1, b2 in zip(bests, bests[1:]))


def test_seed_is_reproducible():
    h1= GASimulation(make_config(selection_method="roulette")).run()
    h2= GASimulation(make_config(selection_method="roulette")).run()
    assert [s.best_fitness for s in h1]==[s.best_fitness for s in h2]


def test_step_after_finish():
    sim= GASimulation(make_config(epochs=1))
    sim.step()
    with pytest.raises(RuntimeError): sim.step()


@pytest.mark.parametrize("overrides", [
    dict(scope=(4.0, -3.0)),
    dict(dimensions=3),
    dict(goal="avg"),
    dict(population=2),
    dict(epochs=0),
    dict(selection_count=0),
    dict(tournament_size=21),
    dict(elitism_rate=1.0),
    dict(mutation_rate=1.5),
])
def test_invalid_config(overrides):
    with pytest.raises(ValueError): make_config(**overrides)


def test_ranking_not_implemented():
    with pytest.raises(ValueError): GASimulation(make_config(selection_method="ranking"))
