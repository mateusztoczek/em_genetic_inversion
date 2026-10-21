import random


def crossover_twopoint(a,b,rng):
    if len(a)<3: raise ValueError("Two points crossover operation requires 3 bits minimum")
    p,q= sorted(rng.sample(range))

    return (a[:p]+b[p:q]+a[q:], b[:p],a[p:q]+b[q:])


def crossover_onepoint(a,b,rng):
    if len(a)<2: raise ValueError("One points crossover requires 2 bits minimum")
    p= rng.randrange(1,len(a))

    return (a[:p]+b[p:],b[:p]+a[p:])


def crossover_granular(a,b,rng):
    ch1=[rng.choice((x,y)) for x,y in zip(a,b)]
    ch2=[rng.choice((x,y)) for x,y in zip(a,b)]
    return ch1, ch2


def crossover_uniform(a,b,rng):
    ch1=[]
    ch2=[]

    for b1,b2 in zip(a,b):
        if rng.random()<0.5:
            ch1.append(b1)
            ch2.append(b2)
        else:
            ch1.append(b2)
            ch2.append(b1)
    
    return ch1,ch2


def crossover_apply(ch1: list[int], ch2: list[int], method: str, rng: random.Random)-> tuple[list[int], list[int]]:
    if not ch1: raise ValueError("first chromosome missing")
    if len(ch1)!=len(ch2): raise ValueError("chromosome are not equal")
    methods={
        "one_point": crossover_onepoint,
        "two_point": crossover_twopoint,
        "uniform": crossover_uniform,
        "granular": crossover_granular
    }

    if method not in methods: raise ValueError(f"Unknown method: {method}")
    return methods[method](ch1,ch2, rng)