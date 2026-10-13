import pytest

from src.core.engine import decode_chromosome

def test_decode_chromosome():
    a,b= -10.0, 10.0

    assert decode_chromosome([0,0,0,0],a,b)==pytest.approx(-10.0)
    assert decode_chromosome([1,1,1,1],a,b)==pytest.approx(10.0)
    assert decode_chromosome([1,0,0,0],a,b)==pytest.approx(2/3)
            