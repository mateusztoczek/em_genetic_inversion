import json
from pathlib import Path

RUN_CONFIG_PATH = Path(__file__).with_name("config.json")

RUN_DEFAULT_CONFIG ={
    "run":{
        "mode": "DEBUG"
    },
    "path":{
        "dir_output": "./output",
        "dir_log": "./logs"
    },
    "display":{
        "decimal_accuracy": 4
    }
}


def load_config(path=RUN_CONFIG_PATH):
    path=Path(path)
    
    config= {
        sec: vals.copy()
        for sec, vals in RUN_DEFAULT_CONFIG.items()
    }
    if not path.exists(): return config

    with path.open("r", encoding="utf-8") as f:
        u_config = json.load(f)
    if not isinstance(u_config, dict):
        raise ValueError("Configuration not a JSON object")

    for sec, vals in u_config.items():
        if sec not in config:
            raise ValueError(f"Unknown config section: {sec}")
        if not isinstance(vals,dict):
            raise ValueError(f"Invalid coonfig section: {sec}")

        for key, val in vals.items():
            if key not in config[sec]:
                raise ValueError(f"Unknown key: {sec}.{key}")
            if not isinstance(val,type(config[sec][key])):
                raise ValueError(f"Invalid type for: {sec}.{key}")
            config[sec][key]=val
    
    return config