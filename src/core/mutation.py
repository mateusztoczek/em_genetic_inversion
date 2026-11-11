import random


def mutation_boundry(ch: list[int], rng: random.Random)-> list[int]:
    if not ch: raise ValueError("Chromosome missing")
    resp=ch.copy()
    p=rng.choice((0,len(ch)-1))
    resp[p]=1-resp[p]

    return resp

def mutation_onepoint(ch: list[int], rng: random.Random)-> list[int]:
    if not ch: raise ValueError("Chromosome missing")
    resp= ch.copy()
    p= rng.randrange(len(resp))
    resp[p]=1-resp[p]

    return resp


def mutation_twopoint(ch: list[int], rng: random.Random)->list[int]:
    if len(ch)<2: raise ValueError("Two points mutation requires 2 bits minimum")
    resp= ch.copy()
    p,q=rng.sample(range(len(resp)),k=2)
    resp[p]=1-resp[p]
    resp[q]=1-resp[q]

    return resp


def mutation_uniform(g: float,scope: tuple[float, float], rng: random.Random, sigma: float=1.0)-> float:
    s_min, s_max=scope
    return rng.uniform(s_min, s_max)


def mutation_swap(ch: list[float], rng: random.Random)->list[float]:
    if len(ch)<2: raise ValueError("Minimum 2 genes required")
    resp= ch.copy()
    p,q=rng.sample(range(len(resp)),k=2)
    resp[p],resp[q]=resp[q],resp[p]
    return resp


def mutation_gauss(g: float,scope: tuple[float, float],rng: random.Random, sigma: float=1.0)-> float:
    if sigma<=0: raise ValueError("Sigma must be greater than 0")
    s_min, s_max=scope
    resp_g=g+ rng.gauss(0,sigma)
    return max(s_min,min(s_max,resp_g))


def binary_mutation_apply(ch: list[int], method: str, rng: random.Random)-> list[int]:
    methods= {
        "one_point": mutation_onepoint,
        "two_point":mutation_twopoint,
        "boundary": mutation_boundry
    }
    if method not in methods: raise ValueError(f"unknown mutation method: {method}")

    return methods[method](ch, rng)


def real_mutation_apply(g: float, method: str, scope: tuple[float, float],sigma: float,rng: random.Random)-> float:
    methods= {
        "uniform": mutation_uniform,
        "gaussian":mutation_gauss
    }
    if method not in methods: raise ValueError(f"unknown mutation method: {method}")

    return methods[method](g,scope, rng, sigma)
