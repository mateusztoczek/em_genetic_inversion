import pytest
import math

from src.core.engine import evaluate_individual, decode_individual, run_algorithm
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


def test_run_algorithm():
    req= {
        "function":{
            "name":"mccormick",
            "goal": "min",
            "dimension": 2,
            "scope":[-3.0,4.0],
            "precision": 0.0001
        }, "options":{
            "population":20,
            "epochs":1,
            "mutation_rate":0.01,
            "croccover_rate":0.6,
            "elitism_rate": 0.2,
            "function_seed": None
        }
    }
    res= run_algorithm(req)
    res_func= get_function("mccormick",2)
    assert len(res.population)==20

    for ind in res:
        assert len(ind.chromosomes)==2
        assert ind.fitness_score is not None
        assert math.isfinite(ind.fitness_score)

        x= decode_individual(ind, -3.0,4.0)

        assert all(-3.0 <=xi <=4.0 for xi in x)
        assert ind.fitness_score== pytest.approx(res_func(x))