import math
import random
from ga_structure import GAIndividual, GAPopulation


def calc_bit_len(a: float, b: float, precision: float) -> int:
    if b-a <=0.0:
        raise ValueError("Scope cant be negative or equals to 0")
    m= math.ceil(math.log2((b-a)/precision+1))

    return m


# TODO: change list of int to bitarray or smt to not waste memory on such stupid thing
def generate_chromosome(m: int)-> list:
    return [random.randint(0,1) for _ in range(m)]


def generate_individual(m: int, dim: int) -> GAIndividual:
    if dim<1: raise ValueError("Minimum 1 dimension is required.")
    if m<1: raise ValueError("Chromosome length cant be smaller than 1.")
    
    return GAIndividual(chromosomes=[generate_chromosome(m) for _ in range (dim)])          


def generate_population(population_size: int, m: int, dim: int) -> GAPopulation:
    if population_size <1: raise ValueError("Population must contain at least one individual.")
    return GAPopulation(population=[generate_individual(m,dim) for _ in range(population_size)])


def run_algorithm(u_params: dict):
    if not isinstance(u_params, dict):
           raise TypeError("Invalid request parameters format.")

    f_params= u_params['function']
    a,b = f_params['scope']
    prec_k= f_params['precision']
    m= calc_bit_len(a, b, prec_k)

