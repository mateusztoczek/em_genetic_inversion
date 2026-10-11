from dataclasses import dataclass, field

@dataclass
class GAIndividual:
    chromosomes: list[list[int]]=field(default_factory=list)
    fitness_score: float | None=None

@dataclass
class GAPopulation:
    population: list[GAIndividual]= field(default_factory=list)
    generation: int=0
    