from dataclasses import dataclass, field
from collections.abc import Iterator

@dataclass
class BinaryIndividual:
    chromosomes: list[list[int]]=field(default_factory=list)
    fitness_score: float | None=None

@dataclass
class RealIndividual:
    chromosomes: list[float]=field(default_factory=list)
    fitness_score: float | None=None


GAIndividual=BinaryIndividual | RealIndividual

@dataclass
class GAPopulation:
    population: list[GAIndividual]= field(default_factory=list)
    generation: int=0

    def __iter__(self)-> Iterator[GAIndividual]:
        return iter(self.population)