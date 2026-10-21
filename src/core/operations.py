from .ga_structure import GAIndividual


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
