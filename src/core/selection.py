from .ga_structure import GAPopulation, GAIndividual


def selection_select_parents(pop: GAPopulation, method: str, count: int, goal: str, tournament_s: int =3)-> list[GAIndividual]:
    if method=="best": return selection_select_best(pop,goal, count)
    raise ValueError(f"Unknown provided method: {method}")


def selection_select_best(pop: GAPopulation, goal: str, count: int)-> list[GAIndividual]:
    if count <1 or count >= len(pop.population): raise ValueError(f"Function must return at least one and less than its size number of individuals. Provided number of returned individuals: {count}")
    if any(ind.fitness_score is None for ind in pop): raise ValueError("every individual in population must have evaluated fitness score")

    def fitnes_func_key(ind: GAIndividual)-> float:
        if ind.fitness_score is None:
            raise ValueError("Individual has no any defined fitness score")
        return ind.fitness_score
        
    if goal=="MIN":
        ordered= sorted(pop, key=fitnes_func_key) 
    elif goal=="MAX":
        ordered= sorted(pop, key=fitnes_func_key, reverse= True)
    else: 
        raise ValueError("Unknown goal command, available commands: MIN/MAX")
    parents= ordered[:count]

    return parents
