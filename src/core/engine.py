from .encoding import decode_individual, calc_bit_len, generate_population
from .ga_structure import GAIndividual, GAPopulation
from .functions import get_function


def evaluate_individual(individual: GAIndividual, ga_function, a, b):
    decoded_i= decode_individual(individual=individual,a=a,b=b)
    fitness= ga_function(decoded_i)
    individual.fitness_score= fitness


def evaluate_population(population: GAPopulation, ga_function,a,b):
    for ind in population:
        evaluate_individual(ind, ga_function,a, b)


def run_algorithm(u_params: dict)-> GAPopulation:
    if not isinstance(u_params, dict):
           raise TypeError("Invalid request parameters format.")

    f_params= u_params['function']
    ga_options= u_params['options']
    a,b = f_params['scope']
    prec_k= f_params['precision']
    dim= f_params['dimension']
    population_s= ga_options['population']
    ga_fun= get_function(f_params["name"], dim)

    m= calc_bit_len(a, b, prec_k)
    pop = generate_population(population_s, m,dim)
    evaluate_population(pop, ga_fun, a, b)

    return pop
