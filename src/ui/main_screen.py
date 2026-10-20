import streamlit as st

from src.ui.config_screen import open_config
from src.ui.constants import FUNCTIONS, SELECTION_METHODS, CROSSOVER_METHODS


def render_main_screen():
    cfg= st.session_state.ga_config
    f= cfg["function"]
    sel= cfg["selection"]
    cx= cfg["crossover"]

    st.title("Algorytm genetyczny")

    with st.container(border=True):
        st.markdown(
            f"**Funkcja:** {FUNCTIONS[f['name']]} ({f['goal']}), {f['dimensions']}D, "
            f"przedział [{f['scope'][0]}, {f['scope'][1]}], dokładność {f['decimal_places']} miejsc  \n"
            f"**Populacja:** {cfg['population']}, **epoki:** {cfg['epochs']}  \n"
            f"**Selekcja:** {SELECTION_METHODS[sel['method']]}"
            + (f" (turniej {sel['tournament_size']})" if sel["method"]== "tournament" else "")
            + (f" ({sel[sel['method']+'_percent']}%)" if sel["method"] in ("best", "worst") else "")
            + f"  \n**Krzyżowanie:** {CROSSOVER_METHODS[cx['method']]}, p={cx['probability']}  \n"
            f"**Inwersja:** {'wł.' if cfg['inversion']['enabled'] else 'wył.'}, "
            f"**elitaryzm:** {'wł.' if cfg['elitism']['enabled'] else 'wył.'}"
        )

    col1, col2= st.columns(2)
    col1.button("Konfiguracja", width="stretch", on_click=open_config)
    if col2.button("Uruchom symulację", type="primary", width="stretch"):
        st.info("Ekran symulacji jeszcze nie istnieje.")
