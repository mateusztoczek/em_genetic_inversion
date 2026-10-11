import math

def calc_bit_len(a: float, b: float, precision: float) -> int:
    if b-a <=0.0:
        raise ValueError("Scope cant be negative or equals to 0")
    m= math.ceil(math.log2((b-a)/precision+1))

    return m


def run_algorithm(u_params: dict):
    if not isinstance(u_params, dict):
           raise TypeError("Invalid request parameters format.")

    f_params= u_params['function']
    a,b = f_params['scope']
    prec_k= f_params['precision']
    m= calc_bit_len(a, b, prec_k)

