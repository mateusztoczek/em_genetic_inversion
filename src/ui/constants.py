FUNCTIONS= {
    "mccormick": "McCormick (2D)",
    "mccormick_neg": "−McCormick (2D, maksymalizacja)",
    "rastrigin": "Rastrigin",
    "cec2014_f9": "CEC 2014 F9",
}

DEFAULT_FUNCTION_CONFIG={
    "rastrigin":{
        "goal":"min",
        "dimensions": 2,
        "scope":[-5.12,5.12],
        "decimal_places":4
    },
    "mccormick":{
        "goal":"min",
        "dimensions": 2,
        "scope":[-3,4],
        "decimal_places":4
    },
    "mccormick_neg":{
        "goal":"max",
        "dimensions": 2,
        "scope":[-3,4],
        "decimal_places":4
    },
    "cec2014_f9":{
        "goal":"min",
        "dimensions": 10,
        "scope":[-100.0,100.0],
        "decimal_places":4
    }
}

CEC_DIMS= [10, 20, 30, 100]

SELECTION_METHODS= {
    "best": "Najlepszych",
    "worst": "Najgorszych",
    "natural": "Naturalna (losowa)",
    "tournament": "Turniejowa",
    "roulette": "Ruletkowa",
}

CROSSOVER_METHODS= {
    "one_point": "Jednopunktowe",
    "two_point": "Dwupunktowe",
    "uniform": "Jednorode",
    "granular": "Ziarniste",
}

CHROMOSOME_MODES={
    "separate": "Osobne operacje dla każdej zmiennej",
    "combined": "Połączone chromosomy"
}

MUTATION_METHODS={
    "one_point": "Jednopunktowe",
    "two_point": "Dwupunktowe",
    "boundary": "Brzegowa"
}

DEFAULT_CONFIG= {
    "function": {
        "name": "rastrigin",
        **DEFAULT_FUNCTION_CONFIG["rastrigin"]
    },
    "population": 20,
    "epochs": 1000,
    "selection": {
        "method": "tournament",
        "best_percent": 50,
        "worst_percent": 50,
        "tournament_size": 3,
    },
    "crossover": {
        "method": "one_point",
        "probability": 0.8,
        "uniform_swap": 0.5,
    },
    "chromosome_mode": "separate",
    "mutation": {"method": "one_point", "probability": 0.2},
    "inversion": {"enabled": True, "probability": 0.2},
    "elitism": {"enabled": True, "rate":0.2},
}
