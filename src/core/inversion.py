import random


def inversion_apply(ch: list[int], rng: random.Random)-> list[int]:
    if len(ch)<2: raise ValueError("Inversion requires 2 bits minimum")
    resp=ch.copy()
    p,q=sorted(rng.sample(range(len(ch)),k=2))
    resp[p:q+1]=reversed(resp[p:q+1])

    return resp 