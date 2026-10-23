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

    st.title("Optymalizator ewolucyjny")
    with st.container(border=True):
        g= "Minimalizacja" if f["goal"] == "min" else "Maksymalizacja"
        st.markdown(
            f"**Funkcja celu:** {FUNCTIONS[f['name']]}  \n"
            f"&emsp;**Cel:** {g}  \n"
            f"&emsp;**Liczba wymiarów:** {f['dimensions']}  \n"
            f"&emsp;**Zakres:** [{f['scope'][0]}, {f['scope'][1]}]  \n"
            f"&emsp;**Precyzja:** {f['decimal_places']} miejsc  \n"
            f"**Populacja:** {cfg['population']}  \n"
            f"**Liczba epok:** {cfg['epochs']}  \n"
            f"**Selekcja:** {SELECTION_METHODS[sel['method']]}"
            + (f" (rozmiar turnieju {sel['tournament_size']})" if sel["method"]== "tournament" else "")
            + (f" ({sel[sel['method']+'_percent']}%)" if sel["method"] in ("best", "worst") else "")
            + f"  \n**Krzyżowanie:** {CROSSOVER_METHODS[cx['method']]}, p={cx['probability']}  \n"
            + f"**Mutacja:** {MUTATION_METHODS[mut['method']]} | p={mut['propability']}  \n"
            + f"**Inwersja:** {'włączona' if cfg['inversion']['enabled'] else 'wyłączona'}"
            + (f" | p={cfg['inversion']['propability']}" if cfg['inversion']['enabled'] else "")
            + f"  \n**Elityzm:** {'włączony' if cfg['elitism']['enabled'] else 'wyłączony'}"
            + (f" | {cfg['elitism']['rate'] * 100:g}%" if cfg['elitism']['enabled'] else "")
        )

    col1, col2= st.columns(2)
    col1.button("Konfiguracja", width="stretch", on_click=open_config)
    if col2.button("Wykonaj", type="primary", width="stretch"):
        try: 
            ga_config=to_ga_config(cfg)
            with st.spinner("myślenie..."):
                s=GASimulation(ga_config)
                s.run()
            st.session_state["simulation"]=s
        except Exception as e: st.exception(e)
        #except ValueError as e: st.error(f"Error config: {e}")
    if "simulation" in st.session_state:
        s = st.session_state["simulation"]

        best= (min(s.history, key=lambda stat: stat.best_fitness)if s.config.goal == "min" else max(s.history, key=lambda stat: stat.best_fitness))
        st.subheader("Wyniki")
        st.metric("Najlepsza otrzyman wartość:", f"{best.best_fitness:.6f}")
        st.write("Najlepsze rozwiązanie:",", ".join(f"x{i} = {x:.6f}" for i, x in enumerate(best.best_x, start=1)))
        st.write("Najlepszy wynik w epoce:", best.epoch)
        st.write("Łączna liczba epok:", s.epoch)

        df= pd.DataFrame([{
                "Epoka": stat.epoch,
                "Najlepszy": stat.best_fitness,
                "Średni": stat.mean_fitness,
                "Odchylenie standardowe": stat.std_fitness,
                "Unikalne osobniki": stat.u_genotype,
            }for stat in s.history])
        
        st.subheader("Przebieg obliczeń")
        st.line_chart(df, x="Epoka", y=["Najlepszy", "Średni"])
        st.subheader("Odchylenie standardowe dla fitness")
        st.line_chart(df, x="Epoka", y="Odchylenie standardowe")
        st.subheader("Różnorodność populacji")
        st.line_chart(df, x="Epoka", y="Unikalne osobniki")