import random

from .functions import GAFunction

def crossover_twopoint(ch1, ch2, rng):
    if len(ch1)!= len(ch2) or len(ch1) < 3: raise ValueError("Invalid chromosome lengths.")
    p,q =sorted(rng.sample(range(1,len(ch1)), k=2))

    return (ch1[:p] + ch2[p:q] + ch1[q:], ch2[:p] + ch1[p:q] + ch2[q:])

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


def crossover_linear(a,b,scope, rng, ga_func, goal):
    if goal not in ("min", "max"): raise ValueError("Unknown goal")
    ch1=[(x+y)/2 for x,y in zip(a,b,strict=True)] 
    ch2=[(1.5*x+0.5*y) for x,y in zip(a,b,strict=True)] 
    ch3=[(-0.5*x-1.5*y) for x,y in zip(a,b,strict=True)] 
    s_min, s_max=scope
    chromosoms=[ch for ch in(ch1,ch2,ch3) if all(s_min<=i<=s_max for i in ch)]
    if len(chromosoms)<2: chromosoms.extend((a.copy(),b.copy()))
    chromosoms.sort(key=ga_func,reverse=(goal=='max'))
    return chromosoms[0].copy(), chromosoms[1].copy()


def crossover_arithmetic(a,b,scope,rng):
    alpha_rng= rng.random()
    ch1=[alpha_rng*x+(1-alpha_rng)*y for x,y in zip(a,b,strict=True)]
    ch2=[(1-alpha_rng)*x +alpha_rng*y for x,y in zip(a,b,strict=True)] 
    return ch1, ch2


def crossover_average(a,b,scope,rng):
    ch=[(x+y)/2 for x,y in zip(a,b,strict=True)]
    return ch, ch.copy()


def crossover_flat(a,b,scope,rng):
    ch1=[]
    ch2=[]
    for x,y in zip(a,b, strict=True):
        ch_min=min(x,y)
        ch_max=max(x,y)
        ch1.append(rng.uniform(ch_min,ch_max))
        ch2.append(rng.uniform(ch_min,ch_max))
    return ch1,ch2

def crossover_blend_alpha(a,b,scope,rng,alpha: float=0.3):
    if alpha <0: raise ValueError("Alpha cant be negative")
    ch1=[]
    ch2=[]
    s_min,s_max=scope
    for x,y in zip(a,b, strict=True):
        ch_smaller,ch_high = sorted((x, y))
        s_diff= ch_high-ch_smaller
        ch_min=max(s_min, ch_smaller- alpha*s_diff)
        ch_max=min(s_max, ch_high+ alpha*s_diff)
        ch1.append(rng.uniform(ch_min,ch_max))
        ch2.append(rng.uniform(ch_min,ch_max))

    return ch1,ch2


def crossover_blend_alpha_beta(a,b,scope,rng,alpha: float=0.3, beta: float=0.3):
    if alpha <0 or beta <0: raise ValueError("Alpha and beta cant be negative")
    ch1=[]
    ch2=[]
    s_min,s_max=scope
    for x,y in zip(a,b, strict=True):
        ch_smaller,ch_high = sorted((x, y))
        s_diff= ch_high-ch_smaller
        ch_min=max(s_min, ch_smaller- alpha*s_diff)
        ch_max=min(s_max, ch_high+ beta*s_diff)
        ch1.append(rng.uniform(ch_min,ch_max))
        ch2.append(rng.uniform(ch_min,ch_max))

    return ch1,ch2


def binary_crossover_apply(ch1: list[int], ch2: list[int], method: str, rng: random.Random)-> tuple[list[int], list[int]]:
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


def real_crossover_apply(ch1: list[float], ch2: list[float], method: str,scope: tuple[float,float], rng: random.Random, alpha: float, beta: float, ga_func: GAFunction, goal: str)-> tuple[list[float], list[float]]:
    if not ch1 or not ch2: raise ValueError("Parent is required")
    if len(ch1)!=len(ch2): raise ValueError("chromosome are not equal")
    
    if method=='blend_alpha': return crossover_blend_alpha(ch1,ch2,scope,rng,alpha)
    if method=='blend_alpha_beta': return crossover_blend_alpha_beta(ch1,ch2,scope,rng,alpha, beta)
    if method=='linear': return crossover_linear(ch1,ch2,scope,rng,ga_func,goal )
    
    othr_methods={
        "arithmetic": crossover_arithmetic,
        "flat": crossover_flat,
        "average": crossover_average
    }

    if method not in othr_methods: raise ValueError(f"Unknown method: {method}")
    return othr_methods[method](ch1,ch2, scope, rng)