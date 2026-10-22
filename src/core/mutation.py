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


def mutation_apply(ch: list[int], method: str, rng: random.Random)-> list[int]:
    methods= {
        "one_point": mutation_onepoint,
        "two_point":mutation_twopoint,
        "boundary": mutation_boundry
    }
    if method not in methods: raise ValueError(f"unknown mutation method: {method}")

    return methods[method](ch, rng)