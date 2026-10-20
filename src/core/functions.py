import benchmark_functions 
from opfunu.cec_based.cec2014 import F92014

import numpy as np


'''
def mccormick(x: list[float])-> float:
    if len(x) != 2: raise ValueError(f"Mccormick function requires exactly 2 variables. Nuber of provided variables: {len(x)}")
    x1, x2= x
    cond1= math.sin((x1+x2))
    cond2=(x1-x2)**2
    cond3= -1.5*x1+2.5*x2+1
    y= cond1+cond2+cond3
    return y

def rastrigin(x:list[float], A: float = 10.0)-> float:
    if not x: raise ValueError("Rastrigin requires at least one variable.")

    cond1= A*len(x)
    cond2=sum([xi**2-A*math.cos(2*math.pi*xi) for xi in x])
    return cond1+cond2    
'''

FUNCTION_NAMES= ("mccormick", "rastigin", "cec2014_f9")


def validate_function(f_name: str, dim: int):
    if f_name not in FUNCTION_NAMES: raise ValueError(f"Unknown function name: {f_name}")
    if dim<1: raise ValueError("At least 1 dimension is required.")
    if f_name=="mccormick" and dim!=2: raise ValueError(f"Mccormick function requires exactly 2 variables. Number of provided variables: {dim}")
    if f_name=="cec2014_f9" and dim not in (10,20,30,100): raise ValueError("Unsupported number of CEC 2014 F9 function dimensions.")


def get_function(f_name: str, dim: int):
    validate_function(f_name, dim)
    if f_name== 'mccormick':
        return benchmark_functions.McCormick()
    if f_name== "rastigin":
        return benchmark_functions.Rastrigin(n_dimensions= dim)
    if f_name=="cec2014_f9":
        f_func= F92014(ndim=dim)

        def cec_function(x):
            return float(f_func.evaluate(np.asarray(x)))
        return cec_function
    raise ValueError(f"Unknown function name: {f_name}")
