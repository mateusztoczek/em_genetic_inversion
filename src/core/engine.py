import copy
import random
from collections.abc import Callable
from dataclasses import dataclass

from .encoding import decode_individual, calc_bit_len, generate_population
from .ga_structure import GAIndividual, GAPopulation
from .functions import get_function, validate_function
from .selection import selection_select_parents, selection_select_ordered
from .operations import crossover_ind, mutation_ind

IMPLEMENTED_SELECTION= ("best", "worst", "natural", "tournament", "roulette")


def evaluate_individual(individual: GAIndividual, ga_function, a, b):
    decoded_i= decode_individual(individual=individual,a=a,b=b)
    fitness= ga_function(decoded_i)
    individual.fitness_score= fitness


def evaluate_population(population: GAPopulation, ga_function,a,b):
    for ind in population:
        evaluate_individual(ind, ga_function,a, b)


@dataclass
class GAConfig:
    function: str
    goal: str
    dimensions: int
    scope: tuple[float, float]
    precision: float
    population: int
    epochs: int
    selection_method: str
    # size of the mating pool; None = as many as needed to refill the population
    selection_count: int | None= None
    tournament_size: int= 3
    # rate is None when the operator is turned off
    elitism_rate: float | None= None
    # not applied yet - crossover, mutation and inversion are not implemented
    chromosome_mode: str= "separate"
    crossover_method: str= "one_point"
    crossover_rate: float= 0.8
    mutation_method: str= 'one_point'
    mutation_rate: float= 0.2
    inversion_rate: float | None= None
    seed: int | None= None

    def __post_init__(self):
        validate_function(self.function, self.dimensions)
        a, b= self.scope
        if a>= b: raise ValueError("Scope start must be lower than scope end.")
        if self.goal not in ("min", "max"): raise ValueError(f"Unknown goal: {self.goal}")
        if self.precision<= 0: raise ValueError("Precision must be positive.")
        if self.population< 3: raise ValueError("Population must contain at least 3 individuals.")
        if self.epochs< 1: raise ValueError("At least 1 epoch is required.")
        if self.selection_count is not None and not 1<= self.selection_count<= self.population:
            raise ValueError("Selection count must be between 1 and population size.")
        if self.selection_method=="tournament" and not 3<= self.tournament_size<= self.population:
            raise ValueError("Tournament size must be between 3 and population size.")
        if self.elitism_rate is not None and not 0<= self.elitism_rate< 1:
            raise ValueError("Elitism rate must be in [0, 1).")
        if self.chromosome_mode not in ("separate", "combined"): raise ValueError("Unknown operation mode")
        for name in ("crossover_rate", "mutation_rate", "inversion_rate"):
            rate= getattr(self, name)
            if rate is not None and not 0<= rate<= 1: raise ValueError(f"{name} must be in [0, 1].")


@dataclass
class EpochStats:
    epoch: int
    best_fitness: float
    mean_fitness: float
    worst_fitness: float
    best_x: list[float]


class GASimulation:
    def __init__(self, config: GAConfig):
        if config.selection_method not in IMPLEMENTED_SELECTION:
            raise ValueError(f"Selection method not implemented: {config.selection_method}")

        self.config= config
        self.rng= random.Random(config.seed)
        self.function= get_function(config.function, config.dimensions)
        self.bit_len= calc_bit_len(*config.scope, config.precision)

        elite= round((config.elitism_rate or 0)*config.population)
        self.elite_count= min(elite, config.population-1)

        self.population= generate_population(config.population, self.bit_len, config.dimensions, self.rng)
        self._evaluate()
        self.history: list[EpochStats]= [self._stats()]

    @property
    def epoch(self) -> int:
        return self.population.generation

    @property
    def finished(self) -> bool:
        return self.epoch>= self.config.epochs

    @property
    def best(self) -> GAIndividual:
        return selection_select_ordered(self.population, "best", self.config.goal, 1)[0]

    def decode(self, individual: GAIndividual) -> list[float]:
        return decode_individual(individual, *self.config.scope)

    def step(self) -> EpochStats:
        if self.finished: raise RuntimeError("Simulation already finished.")
        cfg= self.config

        elite= [copy.deepcopy(ind) for ind in selection_select_ordered(self.population, "best", cfg.goal, self.elite_count)] if self.elite_count else []
        children_count= cfg.population-len(elite)

        pool= selection_select_parents(self.population, cfg.selection_method, cfg.selection_count or children_count,
                                       cfg.goal, self.rng, cfg.tournament_size)
        children= self._reproduce(pool, children_count)

        self.population= GAPopulation(population=elite+children, generation=self.epoch+1)
        self._evaluate()
        stats= self._stats()
        self.history.append(stats)
        return stats

    def run(self, on_epoch: Callable[[EpochStats], None] | None= None) -> list[EpochStats]:
        while not self.finished:
            stats= self.step()
            if on_epoch: on_epoch(stats)
        return self.history

    def _reproduce(self, pool: list[GAIndividual], count: int) -> list[GAIndividual]:
        cfg=self.config
        childs=[]

        while len(childs)<count:
            p1, p2=self.rng.choices(pool,k=2)
            ch1, ch2= crossover_ind(p1, p2,cfg.crossover_method,cfg.chromosome_mode,cfg.crossover_rate,self.rng)
            
            for ch in (ch1,ch2):
                ch=mutation_ind(ch,cfg.mutation_method, cfg.chromosome_mode, cfg.mutation_rate, self.rng)
                childs.append(ch)
                if len(childs)==count: break

        return childs         


    def _evaluate(self):
        evaluate_population(self.population, self.function, *self.config.scope)

    def _stats(self) -> EpochStats:
        best= self.best
        assert best.fitness_score is not None, "best individual doent have fittness score, must have one to run calculations"
        scores= [ind.fitness_score for ind in self.population if ind.fitness_score is not None]
        return EpochStats(
            epoch=self.epoch,
            best_fitness=best.fitness_score,
            mean_fitness=sum(scores)/len(scores),
            worst_fitness=max(scores) if self.config.goal=="min" else min(scores),
            best_x=self.decode(best),
        )
