import random
from ..ga_structure import GAPopulation, RealIndividual


def generate_real_individual(dim: int,scope: tuple[float, float],rng: random.Random)->RealIndividual:
    if dim<1: raise ValueError("Min 1 dimension is required")
    a,b =scope
    if a>=b: raise ValueError("Scope start must be smaller than scope end")

    return RealIndividual(chromosomes=[rng.uniform(a,b) for _ in range(dim)])


def generate_real_population(population_size: int,dim: int,scope: tuple[float, float],rng: random.Random) ->GAPopulation:
    if population_size<1: raise ValueError("Population must contain at least one individual")

    return GAPopulation(population=[generate_real_individual(dim, scope, rng)for _ in range(population_size)])