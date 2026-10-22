import streamlit as st
import pandas as pd
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
            f"**elitaryzm:** {'wł.' if cfg['elitism']['enabled'] else 'wył.'}\n"
            f"**Tryb chromosomów:** {CHROMOSOME_MODES[ch_mode]}  \n"
            f"**Mutacja:** {MUTATION_METHODS[mut['method']]}, p={mut['propability']}  \n"
        )

    col1, col2= st.columns(2)
    col1.button("Konfiguracja", width="stretch", on_click=open_config)
    if col2.button("Uruchom symulację", type="primary", width="stretch"):
        try: 
            ga_config=to_ga_config(cfg)
            s=GASimulation(ga_config)
            s.run()
            st.session_state["simulation"]=s
        except Exception as e: st.exception(e)
        #except ValueError as e: st.error(f"Error config: {e}")
    if "simulation" in st.session_state:
        s = st.session_state["simulation"]

        best= (min(s.history, key=lambda stat: stat.best_fitness)if s.config.goal == "min" else max(s.history, key=lambda stat: stat.best_fitness))

        st.metric("best fitness", f"{best.best_fitness:.6f}")
        st.write("best x:", [f"{x:.6f}" for x in best.best_x])
        st.write("found optimum in epoch:", best.epoch)
        st.write("all epoch:", s.epoch)

        df= pd.DataFrame([{
                "Epoka": stat.epoch,
                "Najlepszy": stat.best_fitness,
                "Średni": stat.mean_fitness,
                "Odchylenie standardowe": stat.std_fitness,
                "Unikalne osobniki": stat.u_genotype,
            }for stat in s.history])
        
        st.subheader("Poptimus")
        st.line_chart(df, x="Epoka", y=["Najlepszy", "Średni"])
        st.subheader("std fitness")
        st.line_chart(df, x="Epoka", y="Odchylenie standardowe")
        st.subheader("gen variaty")
        st.line_chart(df, x="Epoka", y="Unikalne osobniki")