from .ga_structure import GAPopulation, GAIndividual


def selection_select_parents(pop: GAPopulation, method: str, count: int, goal: str, tournament_s: int =3)-> list[GAIndividual]:
    if method in ["worst", "best"]:  return selection_select_ordered(pop,method, goal, count)

    raise ValueError(f"Unknown provided method: {method}")


def selection_select_ordered(pop: GAPopulation, method: str, goal: str, count: int)-> list[GAIndividual]:
    if count <1 or count > len(pop.population): raise ValueError(f"Function must return at least one and less than its size number of individuals. Provided number of returned individuals: {count}")
    if any(ind.fitness_score is None for ind in pop): raise ValueError("every individual in population must have evaluated fitness score")
    if goal not in ["min",'max']: raise ValueError("Unknown function")

    def fitnes_func_key(ind: GAIndividual)-> float:
        if ind.fitness_score is None:
            raise ValueError("Individual has no any defined fitness score")
        return ind.fitness_score
        
    ordered= sorted(pop, key=fitnes_func_key, reverse=(goal=="max")) 
    if method=="best": return ordered[:count]
    if method =='worst': return ordered[-count:][::-1]

    '''this default return is so ass but i love it'''
    raise ValueError(f"Unknown method: {method}")

    
