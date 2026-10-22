import random
import pytest
from src.core.mutation import mutation_apply
from src.core.crossover import crossover_apply
from src.core.inversion import inversion_apply


@pytest.mark.parametrize("method", ["one_point","two_point","three_point","uniform","granular"])
def test_crossover(method):
    a=[0]*12
    b=[1]*12
    ch1,ch2= crossover_apply(a, b, method, random.Random(42))

    assert len(ch1)==len(a)
    assert len(ch2)==len(b)
    assert all(bit in(0,1) for bit in ch1)
    assert all(bit in(0,1) for bit in ch2)
    assert a==[0]*12
    assert b==[1]*12
    assert ch1 is not a
    assert ch2 is not b


@pytest.mark.parametrize("method,expected",[
    ("one_point",1),
    ("two_point",2),
    ("boundary",1)
])
def test_mutation(method, expected):
    og_data= [0,1,0,1,1,0,0,1]
    resp =mutation_apply(og_data, method,random.Random(42))
    diff= [i for i in range(len(og_data)) if og_data[i]!= resp[i]]

    assert len(diff)==expected
    assert len(resp)==len(og_data)
    assert og_data== [0,1,0,1,1,0,0,1]
    if method== "boundary": assert diff[0] in (0,len(og_data)-1)


def test_inversion():
    og_data= [1,0,0,1,1,0,1,0]
    resp= inversion_apply(og_data, random.Random(42))

    assert len(resp)==len(og_data)
    assert sorted(resp)== sorted(og_data)
    assert og_data== [1,0,0,1,1,0,1,0]