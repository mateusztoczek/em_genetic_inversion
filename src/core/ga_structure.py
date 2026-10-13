from dataclasses import dataclass, field
from collections.abc import Iterator

@dataclass
class GAIndividual:
    chromosomes: list[list[int]]=field(default_factory=list)
    fitness_score: float | None=None

    def __iter__(self)-> Iterator[list[int]]:
        return iter(self.chromosomes)


@dataclass
class GAPopulation:
    population: list[GAIndividual]= field(default_factory=list)
    generation: int=0

    def __iter__(self)-> Iterator[GAIndividual]:
        return iter(self.population)