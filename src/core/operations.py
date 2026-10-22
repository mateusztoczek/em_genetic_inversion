import random
from .ga_structure import GAIndividual
from .crossover import crossover_apply
from .mutation import mutation_apply


def _chromosome_as_segments(ind: GAIndividual, ch_mode: str) -> list[list[int]]:
    if ch_mode=='separate': return [chrom.copy() for chrom in ind.chromosomes]
    if ch_mode=='combined': 
        resp= [bit for chrom in ind.chromosomes for bit in chrom ]
        return [resp]
    
    raise ValueError(f'Unkcnow chromosome mode: {ch_mode}')


def _chromosome_as_ind(segments: list[list[int]], temp_chromosome: GAIndividual, ch_mode: str) -> GAIndividual:
    chrom_len= [len(chrom) for chrom in temp_chromosome]
    if ch_mode=='separate':
        if len(segments)!= len(chrom_len): raise ValueError("Invalid chromosome number")
        if any(len(chrom)!= chrom_size for chrom, chrom_size in zip(segments, chrom_len)): raise ValueError("Chromosome length has changed")
        return GAIndividual(chromosomes=segments)

    if ch_mode=='combined':
        if len(segments)!=1: raise ValueError(f"Expencted one chromosome, got {len(segments)}")
        single_chromosome= segments[0]
        ind_chromosomes= []
        off=0
        if len(single_chromosome)!=sum(chrom_len): raise ValueError("Chromosome length has changed")

        for chrom_size in chrom_len:
            ind_chromosomes.append(single_chromosome[off:off+chrom_size])
            off+= chrom_size
        
        return GAIndividual(chromosomes=ind_chromosomes)
    raise ValueError(f"Unknown chromosome mode: {ch_mode}")


def crossover_ind(p1: GAIndividual, p2: GAIndividual, method: str, ch_mode: str, propability: float, rng: random.Random)-> tuple[GAIndividual, GAIndividual]:
    segment1= _chromosome_as_segments(p1, ch_mode)
    segment2= _chromosome_as_segments(p2, ch_mode)
    ch1_segments=[]
    ch2_segments=[]
    for ch1,ch2 in zip(segment1, segment2, strict=True):
        if rng.random()<propability: resp_ch1, resp_ch2= crossover_apply(ch1, ch2,method,rng)
        else: 
            resp_ch1= ch1.copy()
            resp_ch2=ch2.copy()
        ch1_segments.append(resp_ch1)
        ch2_segments.append(resp_ch2)
    final_ch1=_chromosome_as_ind(ch1_segments,p1,ch_mode)
    final_ch2=_chromosome_as_ind(ch2_segments,p2,ch_mode)

    return final_ch1, final_ch2


def mutation_ind(ind: GAIndividual, method: str, ch_mode: str, propability: float, rng: random.Random)-> GAIndividual:
    segment= _chromosome_as_segments(ind,ch_mode)
    resp_target=[]
    for ch in segment:
        if rng.random()<propability: resp_ch=mutation_apply(ch, method, rng)
        else: resp_ch= ch.copy()
        resp_target.append(resp_ch)

    return _chromosome_as_ind(resp_target,ind,ch_mode)