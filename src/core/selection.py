from .ga_structure import GAPopulation, GAIndividual
import random


def selection_select_parents(pop: GAPopulation, method: str, count: int, goal: str, rng: random.Random, tournament_s: int =3)-> list[GAIndividual]:
    if method in ["worst", "best"]:  return selection_select_ordered(pop,method, goal, count)
    if method=='natural': return selection_select_random(pop, count,rng)
    if method=="tournament": return selection_select_tournament(pop,goal, count, tournament_s, rng)
    if method=="roulette": return selection_select_roulette(pop, goal, count, rng)
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

    raise ValueError(f"Unknown method: {method}")


def selection_select_random(pop: GAPopulation, count: int, rng: random.Random)-> list[GAIndividual]:
    if count <1 or count > len(pop.population): raise ValueError(f"Function must return at least one and less than its size number of individuals. Provided number of returned individuals: {count}")
    if any(ind.fitness_score is None for ind in pop): raise ValueError("every individual in population must have evaluated fitness score")
    parents= rng.choices(pop.population, k=count)
    return parents   


def selection_select_tournament(pop: GAPopulation, goal: str, count: int, tournament_s: int, rng: random.Random)-> list[GAIndividual]:
    if count <1 or count > len(pop.population): raise ValueError(f"Function must return at least one and less than its size number of individuals. Provided number of returned individuals: {count}")
    if not 2< tournament_s<=len(pop.population): raise ValueError("Invalid tournament size")
    if any(ind.fitness_score is None for ind in pop): raise ValueError("every individual in population must have evaluated fitness score")
    if goal not in ["min",'max']: raise ValueError("Unknown function")

    def fitnes_func_key(ind: GAIndividual)-> float:
        if ind.fitness_score is None:
            raise ValueError("Individual has no any defined fitness score")
        return ind.fitness_score

    parents=[]
    for _ in range(count):
        cont= rng.sample(pop.population, k=tournament_s)
        if goal=="min": win_p= min(cont, key=fitnes_func_key)
        else: win_p= max(cont, key=fitnes_func_key)

        parents.append(win_p)
    return parents


def selection_select_roulette(pop: GAPopulation, goal:str, count: int, rng: random.Random)-> list[GAIndividual]:
    if count <1 or count > len(pop.population): raise ValueError(f"Function must return at least one and less than its size number of individuals. Provided number of returned individuals: {count}")
    if any(ind.fitness_score is None for ind in pop): raise ValueError("every individual in population must have evaluated fitness score")
    if goal not in ["min",'max']: raise ValueError("Unknown function")

    scores= [ind.fitness_score for ind in pop]
    # shift scores so the worst individual gets 0 - works for negative fitness and for minimization
    if goal=="max": weights= [s-min(scores) for s in scores]
    else: weights= [max(scores)-s for s in scores]

    if sum(weights)==0: return rng.choices(pop.population, k=count)
    return rng.choices(pop.population, weights=weights, k=count)
