from src.core.engine import GAConfig


def selected_count(percent: int, population: int) -> int:
    return max(1,round(percent/100*population))


def to_ga_config(cfg: dict) -> GAConfig:
    f= cfg["function"]
    sel= cfg["selection"]

    selection_count= None
    if sel["method"] in ("best", "worst"):
        selection_count= selected_count(sel[f"{sel['method']}_percent"], cfg["population"])

    return GAConfig(
        function=f["name"],
        goal=f["goal"],
        dimensions=f["dimensions"],
        scope=(f["scope"][0], f["scope"][1]),
        precision=10**-f["decimal_places"],
        population=cfg["population"],
        epochs=cfg["epochs"],
        selection_method=sel["method"],
        selection_count=selection_count,
        tournament_size=sel["tournament_size"],
        chromosome_mode=cfg["chromosome_mode"],
        elitism_rate=cfg["elitism"]["rate"] if cfg["elitism"]["enabled"] else None,
        crossover_method=cfg["crossover"]["method"],
        crossover_rate=cfg["crossover"]["probability"],
        mutation_method=cfg["mutation"]["method"],
        mutation_rate=cfg["mutation"]["probability"],
        inversion_rate=cfg["inversion"]["probability"] if cfg["inversion"]["enabled"] else None,
    )
