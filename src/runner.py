from src.config.loader import load_config
from src.core.engine import run_algorithm
import sys
import argparse
import shlex


def parse_request(input_raw:str)-> dict:
    token_list= shlex.split(input_raw)
    if not token_list or token_list[0]!= "run":
        raise ValueError("Unknown command")

    # return {"request":input_raw}


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
            result= run_algorithm(u_params, config)
            print(f"Result: {result}")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Ann error occured: {e}")