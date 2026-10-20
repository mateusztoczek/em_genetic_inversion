import random

import pytest

from src.core.ga_structure import GAIndividual, GAPopulation
from src.core.selection import selection_select_roulette, selection_select_parents


def make_pop(scores: list[float]) -> GAPopulation:
    return GAPopulation(population=[GAIndividual(fitness_score=s) for s in scores])


def test_roulette_returns_count():
    pop= make_pop([1.0, 2.0, 3.0, 4.0])
    parents= selection_select_roulette(pop, "max", 4, random.Random(0))
    assert len(parents)==4
    assert all(p in pop.population for p in parents)


def test_roulette_never_picks_worst():
    pop= make_pop([-5.0, 0.0, 3.0])
    rng= random.Random(1)
    worst_max= pop.population[0]
    worst_min= pop.population[2]

    assert worst_max not in selection_select_roulette(pop, "max", 3, rng)
    assert worst_min not in selection_select_roulette(pop, "min", 3, rng)


def test_roulette_prefers_better():
    pop= make_pop([0.0, 1.0, 9.0])
    rng= random.Random(2)
    picks= [p for _ in range(1000) for p in selection_select_roulette(pop, "max", 3, rng)]
    # weights 0:1:9 -> best should get ~90% of picks
    assert picks.count(pop.population[2])/len(picks)==pytest.approx(0.9, abs=0.03)


def test_roulette_equal_scores_uniform():
    pop= make_pop([2.0, 2.0, 2.0])
    parents= selection_select_roulette(pop, "min", 3, random.Random(3))
    assert len(parents)==3


def test_roulette_invalid():
    pop= make_pop([1.0, 2.0])
    with pytest.raises(ValueError): selection_select_roulette(pop, "max", 0, random.Random())
    with pytest.raises(ValueError): selection_select_roulette(pop, "bad", 1, random.Random())
    with pytest.raises(ValueError): selection_select_roulette(make_pop([1.0, None]), "max", 1, random.Random())


def test_dispatch_roulette():
    pop= make_pop([1.0, 2.0, 3.0])
    assert len(selection_select_parents(pop, "roulette", 2, "max", random.Random(4)))==2
