FUNCTIONS= {
    "mccormick": "McCormick (2D)",
    "rastigin": "Rastrigin",
    "cec2014_f9": "CEC 2014 F9",
}
CEC_DIMS= [10, 20, 30, 100]

SELECTION_METHODS= {
    "best": "Najlepszych",
    "worst": "Najgorszych",
    "natural": "Naturalna (losowa)",
    "tournament": "Turniejowa",
    "roulette": "Ruletkowa",
    "ranking": "Rankingowa (niezaimplementowana)",
}
RANK_METHODS= {
    "ordinal": "Kolejne (1, 2, 3, 4)",
    "average": "Średnia przy remisach (1, 2.5, 2.5, 4)",
    "min": "Minimalna przy remisach (1, 2, 2, 4)",
    "dense": "Gęsta (1, 2, 2, 3)",
}
COPIES_FUNCTIONS= {
    "linear": "Liniowa",
    "exponential": "Wykładnicza",
}

CROSSOVER_METHODS= {
    "one_point": "Jednopunktowe",
    "two_point": "Dwupunktowe",
    "three_point": "Trzypunktowe",
    "uniform": "Jednorodne",
}

# not implemented yet - shown as read-only values
MUTATION_HARDCODED= {"method": "Jednopunktowa", "probability": 0.2}
INVERSION_PROBABILITY= 0.01
ELITISM_RATE= 0.2

DEFAULT_CONFIG= {
    "function": {
        "name": "rastigin",
        "goal": "min",
        "dimensions": 2,
        "scope": [-5.12, 5.12],
        "decimal_places": 4,
    },
    "population": 20,
    "epochs": 1000,
    "selection": {
        "method": "tournament",
        "best_percent": 50,
        "worst_percent": 50,
        "tournament_size": 3,
        "rank_method": "ordinal",
        "copies_function": "linear",
        "max_copies": 2,
        "exp_base": 0.9,
    },
    "crossover": {
        "method": "one_point",
        "probability": 0.8,
        "uniform_swap": 0.5,
    },
    "mutation": {"method": "one_point", "probability": MUTATION_HARDCODED["probability"]},
    "inversion": {"enabled": True, "probability": INVERSION_PROBABILITY},
    "elitism": {"enabled": True, "rate": ELITISM_RATE},
}
