from src.config.loader import load_config
from src.core.engine import run_algorithm
import sys
import argparse
import shlex


def parse_request(input_raw:str)-> dict:
    input_list= shlex.split(input_raw)
    if not input_list or input_list[0]!= "run":
        raise ValueError("Unknown command")

    parser=argparse.ArgumentParser(prog="run")
    parser.add_argument("--function",type=str, required=True)
    parser.add_argument("--goal",type=str, default="min")
    parser.add_argument("--range_min",type=float, default=100.0)
    parser.add_argument("--range_max",type=float, default=100.0)    
    parser.add_argument("--dim",type=int, default=2)
    parser.add_argument("--precision",type=float, default=0.0001)
    parser.add_argument("--epoch",type=int, default=1000)
    parser.add_argument("--pop_size",type=int, default=20)
    parser.add_argument("--mutation_prop",type=float, default=0.2)
    parser.add_argument("--crossover_prop",type=float, default=0.8)
    parser.add_argument("--inversion_prop",type=float, default=0.01)
    parser.add_argument("--elit_prop",type=float, default=0.2)
    parser.add_argument("--seed",type=int, default=None)

    args= parser.parse_args(input_list[1:])

    if args.range_min>=args.range_max:
        parser.error("Scope range cant be 0.")
    if args.epoch<=0:
        parser.error("Epoch cant be less than 1.")
    if args.dim<1:
        parser.error("At least 1 dimention is required.")
    if args.pop_size<3:
        parser.error("Population too small.")
    for arg in (args.mutation_prop, args.crossover_prop, 
                args.inversion_prop, args.elit_prop):
        if 0 > arg > 1:
            parser.error("All propabilities must be between 0 and 1.")
            
    # return {"request":input_raw}
    return {
        "function":{
            "name": args.function,
            "goal": args.goal,
            "dimensions": args.dim,
            "scope": [args.range_min, args.range_max],
            "precision": args.precision
        },
        "options":{
            "population": args.pop_size,
            "epochs": args.epoch,
            "mutation_rate": args.mutation_prop,
            "crossover_rate": args.crossover_prop,
            "inversion_rate": args.inversion_prop,
            "elitism_rate": args.elit_prop,
            "function_seed": args.seed
        }
    }


def run():
    try:
        config = load_config()
    except Exception as e:
        sys.exit(1)

    while True:
        try:
            u_input= input("Waiting for input... ").strip()
            if not u_input: continue
            if u_input.lower() == 'exit':
                break
            u_params= parse_request(u_input)
            result= run_algorithm(u_params)
            print(f"Result: {result}")

        except SystemExit:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Ann error occured: {e}")