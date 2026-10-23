import streamlit as st

from src.core.encoding import calc_bit_len
from src.ui.engine_mapping import selected_count, to_ga_config
from src.ui.constants import (
    FUNCTIONS, DEFAULT_FUNCTION_CONFIG, CEC_DIMS, SELECTION_METHODS, RANK_METHODS, COPIES_FUNCTIONS, CROSSOVER_METHODS,
    MUTATION_METHODS, CHROMOSOME_MODES,
)


def seed(key: str, value):
    # widget keys get dropped by streamlit when the widget is not rendered, so refill them from saved config
    if key not in st.session_state:
        st.session_state[key]= value


def apply_function_defaults():
    s= st.session_state
    n = s["w_function"]
    funcdef= DEFAULT_FUNCTION_CONFIG[n]

    s["w_goal"] = funcdef["goal"]
    s["w_range_min"]=funcdef["scope"][0]
    s["w_range_max"]=funcdef["scope"][1]
    s["w_decimal_places"]=funcdef["decimal_places"]
    dim =funcdef["dimensions"]
    s["w_dim"]= dim
    s["w_dim_cec"]= dim if dim in CEC_DIMS else CEC_DIMS[0]


def open_config():
    for key in [k for k in st.session_state if k.startswith("w_")]:
        del st.session_state[key]
    st.session_state.config_errors= []
    st.session_state.screen= "config"


def cancel_config():
    st.session_state.config_errors= []
    st.session_state.screen= "main"


def build_config() -> dict:
    s= st.session_state
    old= s.ga_config
    f_old, sel_old, cx_old= old["function"], old["selection"], old["crossover"]

    name= s.get("w_function", f_old["name"])
    if name== "mccormick": dim= 2
    elif name== "cec2014_f9": dim= s.get("w_dim_cec", f_old["dimensions"])
    else: dim= s.get("w_dim", f_old["dimensions"])

    return {
        "function": {
            "name": name,
            "goal": s.get("w_goal", f_old["goal"]),
            "dimensions": dim,
            "scope": [s.get("w_range_min", f_old["scope"][0]), s.get("w_range_max", f_old["scope"][1])],
            "decimal_places": s.get("w_decimal_places", f_old["decimal_places"]),
        },
        "population": s.get("w_population", old["population"]),
        "epochs": s.get("w_epochs", old["epochs"]),
        "selection": {
            "method": s.get("w_sel_method", sel_old["method"]),
            "best_percent": s.get("w_best_percent", sel_old["best_percent"]),
            "worst_percent": s.get("w_worst_percent", sel_old["worst_percent"]),
            "tournament_size": s.get("w_tournament_size", sel_old["tournament_size"]),
            "rank_method": s.get("w_rank_method", sel_old["rank_method"]),
            "copies_function": s.get("w_copies_function", sel_old["copies_function"]),
            "max_copies": s.get("w_max_copies", sel_old["max_copies"]),
            "exp_base": s.get("w_exp_base", sel_old["exp_base"]),
        },
        "crossover": {
            "method": s.get("w_cx_method", cx_old["method"]),
            "probability": s.get("w_cx_probability", cx_old["probability"]),
            "uniform_swap": s.get("w_uniform_swap", cx_old["uniform_swap"]),
        },
        "chromosome_mode":s.get("w_chromosome_mode",old.get("chromosome_mode","separate")),
        "mutation":{
            "method":s.get("w_mutation_method",old["mutation"]["method"]),
            "propability":s.get("w_mutation_propability",old["mutation"]["propability"])
        },
        "inversion":{
            "enabled":s.get("w_inversion",old["inversion"]["enabled"]),
            "propability":s.get("w_inversion_propability",old["inversion"]["propability"])
        },
        "elitism":{
            "enabled":s.get("w_elitism",old["elitism"]["enabled"]),
            "rate":s.get("w_elitism_percent",round(old["elitism"]["rate"]*100))/100
        }        
    }


def save_config():
    cfg= build_config()
    try:
        to_ga_config(cfg)
    except ValueError as e:
        st.session_state.config_errors= [f"Błędna konfiguracja: {e}"]
        return
    st.session_state.config_errors= []
    st.session_state.ga_config= cfg
    st.session_state.pop("simulation",None)
    st.session_state.screen= "main"


def render_function_section(cfg: dict):
    f= cfg["function"]
    st.subheader("Funkcja")

    seed("w_function", f["name"])
    seed("w_goal", f["goal"])
    seed("w_dim", f["dimensions"])
    seed("w_dim_cec", f["dimensions"] if f["dimensions"] in CEC_DIMS else CEC_DIMS[0])
    seed("w_range_min", float(f["scope"][0]))
    seed("w_range_max", float(f["scope"][1]))
    seed("w_decimal_places", f["decimal_places"])
    seed("w_chromosome_mode", cfg.get("chromosome_mode","separate"))

    st.selectbox("Tryb operacji na chromosomach", list(CHROMOSOME_MODES), format_func=CHROMOSOME_MODES.get, key="w_chromosome_mode")

    col1, col2= st.columns(2)
    #name= col1.selectbox("Funkcja celu", list(FUNCTIONS), format_func=FUNCTIONS.get, key="w_function")
    name= col1.selectbox("Funkcja celu", list(FUNCTIONS), format_func=FUNCTIONS.get, key="w_function", on_change=apply_function_defaults)    
    col2.radio("Cel", ["min", "max"], horizontal=True, key="w_goal")

    if name== "mccormick":
        dim= col1.number_input("Liczba wymiarów", value=2, disabled=True, help="McCormick jest zdefiniowana tylko dla 2 zmiennych.")
    elif name== "cec2014_f9":
        dim= col1.selectbox("Liczba wymiarów", CEC_DIMS, key="w_dim_cec")
    else:
        dim= col1.number_input("Liczba wymiarów", min_value=1, step=1, key="w_dim")

    col_a, col_b= st.columns(2)
    a= col_a.number_input("Przedział: od", key="w_range_min")
    b= col_b.number_input("Przedział: do", key="w_range_max")

    places= st.number_input("Dokładność reprezentacji binarnej (miejsca po przecinku)",
                            min_value=0, max_value=12, step=1, key="w_decimal_places")
    try:
        m= calc_bit_len(a, b, 10**-places)
        st.caption(f"Długość chromosomu: {m} bitów na zmienną, łącznie {m*dim} bitów na osobnika.")
    except ValueError:
        st.caption("Nie da się policzyć długości chromosomu dla takiego przedziału.")


def render_algorithm_section(cfg: dict):
    st.subheader("Algorytm")
    seed("w_population", cfg["population"])
    seed("w_epochs", cfg["epochs"])

    col1, col2= st.columns(2)
    col1.number_input("Wielkość populacji", min_value=3, step=1, key="w_population")
    col2.number_input("Liczba epok", min_value=1, step=1, key="w_epochs")


def render_selection_section(cfg: dict):
    sel= cfg["selection"]
    st.subheader("Selekcja")

    seed("w_sel_method", sel["method"])
    method= st.selectbox("Metoda selekcji", list(SELECTION_METHODS), format_func=SELECTION_METHODS.get, key="w_sel_method")

    if method in ("best", "worst"):
        key= f"w_{method}_percent"
        seed(key, sel[f"{method}_percent"])
        label= "najlepszych" if method== "best" else "najgorszych"
        percent= st.number_input(f"Procent {label} osobników [%]", min_value=1, max_value=100, step=1, key=key)
        population= st.session_state.get("w_population", cfg["population"])
        st.caption(f"Przy populacji {population} to {selected_count(percent, population)} osobników.")

    if method== "tournament":
        seed("w_tournament_size", sel["tournament_size"])
        st.number_input("Rozmiar turnieju", min_value=3, step=1, key="w_tournament_size")

    if method== "ranking":
        st.warning("Selekcja rankingowa nie jest jeszcze zaimplementowana w silniku, ale jej parametry już się zapisują.")
        seed("w_rank_method", sel["rank_method"])
        seed("w_copies_function", sel["copies_function"])
        seed("w_max_copies", sel["max_copies"])
        seed("w_exp_base", sel["exp_base"])

        st.selectbox("Sposób nadawania rang (1 = najlepszy)", list(RANK_METHODS), format_func=RANK_METHODS.get, key="w_rank_method")
        col1, col2= st.columns(2)
        copies_fn= col1.selectbox("Funkcja liczby kopii", list(COPIES_FUNCTIONS), format_func=COPIES_FUNCTIONS.get, key="w_copies_function")
        col2.number_input("Maks. liczba kopii (c_max)", min_value=1, step=1, key="w_max_copies")

        if copies_fn== "linear":
            st.latex(r"k(r) = \mathrm{round}\left(c_{max} \cdot \frac{N - r + 1}{N}\right)")
        else:
            st.number_input("Podstawa q", min_value=0.01, max_value=0.99, step=0.01, key="w_exp_base")
            st.latex(r"k(r) = \mathrm{round}\left(c_{max} \cdot q^{\,r-1}\right)")


def render_crossover_section(cfg: dict):
    cx= cfg["crossover"]
    st.subheader("Krzyżowanie")
    st.caption("Krzyżowanie nie jest jeszcze zaimplementowane w silniku.")

    seed("w_cx_method", cx["method"])
    seed("w_cx_probability", cx["probability"])

    col1, col2= st.columns(2)
    method= col1.selectbox("Metoda krzyżowania", list(CROSSOVER_METHODS), format_func=CROSSOVER_METHODS.get, key="w_cx_method")
    col2.slider("Prawdopodobieństwo krzyżowania", 0.0, 1.0, step=0.01, key="w_cx_probability")

    if method== "uniform": seed("w_uniform_swap", cx["uniform_swap"])

def render_operators_section(cfg: dict):
    elitism= cfg["elitism"]
    mutation= cfg["mutation"]
    inversion= cfg["inversion"]
    
    st.subheader("Mutacja")
    seed("w_mutation_method", mutation["method"])
    seed("w_mutation_propability", mutation["propability"])

    col1,col2 = st.columns(2)
    col1.selectbox("Metoda mutacji", list(MUTATION_METHODS),format_func=MUTATION_METHODS.get,key="w_mutation_method",)
    col2.slider("Prawdopodobieństwo mutacji",min_value=0.0,max_value=1.0,step=0.01,key="w_mutation_propability",)

    st.subheader("Inwersja")
    seed("w_inversion", inversion["enabled"])
    seed("w_inversion_propability", inversion["propability"])

    col1,col2=st.columns(2)
    col1.toggle("Możliwa inwersja", key="w_inversion",)
    col2.slider("Prawdopodobieństwo inwersji",min_value=0.0,max_value=1.0,step=0.01,key="w_inversion_propability",disabled=not st.session_state.w_inversion,)

    st.subheader("Strategia elitarna")
    seed("w_elitism",elitism["enabled"])
    seed("w_elitism_percent", round(elitism["rate"]*100))

    col1, col2 = st.columns(2)
    col1.toggle("Włącz strategię elitarną",key="w_elitism",)
    col2.slider("Odsetek najlepszych w procentach",min_value=0,max_value=99, step=1,key="w_elitism_percent",disabled=not st.session_state.w_elitism,)


def render_config_screen():
    cfg= st.session_state.ga_config
    st.title("Konfiguracja algorytmu genetycznego")

    render_function_section(cfg)
    st.divider()
    render_algorithm_section(cfg)
    st.divider()
    render_selection_section(cfg)
    st.divider()
    render_crossover_section(cfg)
    st.divider()
    render_operators_section(cfg)
    st.divider()

    for err in st.session_state.config_errors:
        st.error(err)

    col1, col2= st.columns(2)
    col1.button("Zapisz", type="primary", width="stretch", on_click=save_config)
    col2.button("Anuluj", width="stretch", on_click=cancel_config)
