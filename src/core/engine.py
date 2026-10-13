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


def decode_chromosome(chromosome: list, a: float, b: float) -> float:
    if not chromosome: raise ValueError("Cannot decode empty chromosome")
    m= len(chromosome)
    dec_sub= (2**m)-1
    if dec_sub<=0.0: raise ValueError("Division by 0 detected.")
    chromosome_decimal= 0
    for bit in chromosome:
        chromosome_decimal=(chromosome_decimal<<1) | bit
    
    decoded= a+((chromosome_decimal*(b-a))/dec_sub)
    return decoded


def decode_individual(individual: GAIndividual, a: float, b: float) -> list[float]:
    return [decode_chromosome(chromosome, a, b) for chromosome in individual.chromosomes]


def evaluate_individual(individual: GAIndividual, ga_function, a, b):
    decoded_i= decode_individual(individual=individual,a=a,b=b)
    fitness= ga_function(decoded_i)
    individual.fitness_score= fitness


def evaluate_population(population: GAPopulation, ga_function,a,b):
    for ind in population:
        evaluate_individual(ind, ga_function,a, b)



def run_algorithm(u_params: dict):
    if not isinstance(u_params, dict):
           raise TypeError("Invalid request parameters format.")

    f_params= u_params['function']
    a,b = f_params['scope']
    prec_k= f_params['precision']
    m= calc_bit_len(a, b, prec_k)

