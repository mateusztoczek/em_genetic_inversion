import math
import random


def calc_bit_len(a: float, b: float, precision: float) -> int:
    if b-a <=0.0:
        raise ValueError("Scope cant be negative or equals to 0")
    m= math.ceil(math.log2((b-a)/precision+1))

    return m


# TODO: change list of int to bitarray or smt to not waste memory on such stupid thing
def generate_chromosome(m: int)-> list:
    return [random.randint(0,1) for _ in range(m)]


def run_algorithm(u_params: dict):
    if not isinstance(u_params, dict):
           raise TypeError("Invalid request parameters format.")

    f_params= u_params['function']
    a,b = f_params['scope']
    prec_k= f_params['precision']
    m= calc_bit_len(a, b, prec_k)

