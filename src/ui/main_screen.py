import streamlit as st

from src.ui.config_screen import open_config
from src.ui.constants import FUNCTIONS, SELECTION_METHODS, CROSSOVER_METHODS, MUTATION_METHODS, CHROMOSOME_MODES
from .engine_mapping import to_ga_config
from src.core.engine import GASimulation

def render_main_screen():
    cfg= st.session_state.ga_config
    f= cfg["function"]
    sel= cfg["selection"]
    cx= cfg["crossover"]
    mut=cfg["mutation"]
    ch_mode=cfg["chromosome_mode"]

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
            f"**Tryb chromosomów:** {CHROMOSOME_MODES[ch_mode]}  \n"
            f"**Mutacja:** {MUTATION_METHODS[mut['method']]}, "
            f"p={mut['probability']}  \n"
        )

    col1, col2= st.columns(2)
    col1.button("Konfiguracja", width="stretch", on_click=open_config)
    if col2.button("Uruchom symulację", type="primary", width="stretch"):
        try: 
            ga_config=to_ga_config(cfg)
            s=GASimulation(ga_config)
            s.run()
            st.session_state["simulation"]=s
        except ValueError as e: st.error(f"Error config: {e}")
