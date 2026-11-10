import random
from .ga_structure import BinaryIndividual, RealIndividual
from .crossover import binary_crossover_apply, real_crossover_apply
from .mutation import mutation_apply
from .inversion import inversion_apply
from .functions import GAFunction

def _chromosome_as_segments(ind: BinaryIndividual, ch_mode: str) -> list[list[int]]:
    if ch_mode=='separate': return [chrom.copy() for chrom in ind.chromosomes]
    if ch_mode=='combined': 
        resp= [bit for chrom in ind.chromosomes for bit in chrom ]
        return [resp]
    
    raise ValueError(f'Unkcnow chromosome mode: {ch_mode}')


def _chromosome_as_ind(segments: list[list[int]], temp_chromosome: BinaryIndividual, ch_mode: str) -> BinaryIndividual:
    chrom_len= [len(chrom) for chrom in temp_chromosome.chromosomes]
    if ch_mode=='separate':
        if len(segments)!= len(chrom_len): raise ValueError("Invalid chromosome number")
        if any(len(chrom)!= chrom_size for chrom, chrom_size in zip(segments, chrom_len)): raise ValueError("Chromosome length has changed")
        return BinaryIndividual(chromosomes=segments)

    if ch_mode=='combined':
        if len(segments)!=1: raise ValueError(f"Expencted one chromosome, got {len(segments)}")
        single_chromosome= segments[0]
        ind_chromosomes= []
        off=0
        if len(single_chromosome)!=sum(chrom_len): raise ValueError("Chromosome length has changed")

        for chrom_size in chrom_len:
            ind_chromosomes.append(single_chromosome[off:off+chrom_size])
            off+= chrom_size
        
        return BinaryIndividual(chromosomes=ind_chromosomes)
    raise ValueError(f"Unknown chromosome mode: {ch_mode}")


def binary_crossover_ind(p1: BinaryIndividual, p2: BinaryIndividual, method: str, ch_mode: str, probability: float, rng: random.Random)-> tuple[BinaryIndividual, BinaryIndividual]:
    segment1= _chromosome_as_segments(p1, ch_mode)
    segment2= _chromosome_as_segments(p2, ch_mode)
    ch1_segments=[]
    ch2_segments=[]
    for ch1,ch2 in zip(segment1, segment2, strict=True):
        if rng.random()<probability: resp_ch1, resp_ch2= binary_crossover_apply(ch1, ch2,method,rng)
        else: 
            resp_ch1= ch1.copy()
            resp_ch2=ch2.copy()
        ch1_segments.append(resp_ch1)
        ch2_segments.append(resp_ch2)
    final_ch1=_chromosome_as_ind(ch1_segments,p1,ch_mode)
    final_ch2=_chromosome_as_ind(ch2_segments,p2,ch_mode)

    return final_ch1, final_ch2



def real_crossover_ind(p1: RealIndividual, p2: RealIndividual, method: str, probability: float,scope: tuple[float,float], rng: random.Random, alpha: float, beta: float, ga_func: GAFunction, goal: str)-> tuple[RealIndividual, RealIndividual]:
    if len(p1.chromosomes)!=len(p2.chromosomes): raise ValueError("Number of chromosomes not equal")
    if rng.random()<probability: resp_ch1, resp_ch2= real_crossover_apply(p1.chromosomes, p2.chromosomes,method,scope,rng, alpha, beta, ga_func, goal)
    else: 
        resp_ch1= p1.chromosomes.copy()
        resp_ch2=p2.chromosomes.copy()
    
    return RealIndividual(resp_ch1), RealIndividual(resp_ch2)



def binary_mutation_ind(ind: BinaryIndividual, method: str, ch_mode: str, probability: float, rng: random.Random)-> BinaryIndividual:
    segment= _chromosome_as_segments(ind,ch_mode)
    resp_target=[]
    for ch in segment:
        if rng.random()<probability: resp_ch=mutation_apply(ch, method, rng)
        else: resp_ch= ch.copy()
        resp_target.append(resp_ch)

    return _chromosome_as_ind(resp_target,ind,ch_mode)


def inversion_ind(ind: BinaryIndividual, ch_mode: str, probability: float, rng: random.Random)-> BinaryIndividual:
    segment= _chromosome_as_segments(ind,ch_mode)
    resp_target=[]
    for ch in segment:
        if rng.random()<probability: resp_ch=inversion_apply(ch, rng)
        else: resp_ch= ch.copy()
        resp_target.append(resp_ch)

    return _chromosome_as_ind(resp_target,ind,ch_mode)