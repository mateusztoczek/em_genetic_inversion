import streamlit as st
import pandas as pd
from src.ui.config_screen import open_config
from src.ui.constants import FUNCTIONS, SELECTION_METHODS, CROSSOVER_METHODS, MUTATION_METHODS, CHROMOSOME_MODES
from .engine_mapping import to_ga_config
from src.core.storage import run_with_recording, DEFAULT_DB_PATH

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
            f"**Tryb operacji na chromosomach:** {CHROMOSOME_MODES[ch_mode]}  \n"
            f"**Funkcja celu:** {FUNCTIONS[f['name']]}  \n"
            f"&emsp;**Cel:** {g}  \n"
            f"&emsp;**Liczba wymiarów:** {f['dimensions']}  \n"
            f"&emsp;**Zakres:** [{f['scope'][0]}, {f['scope'][1]}]  \n"
            f"&emsp;**Precyzja:** {f['decimal_places']} miejsc  \n"
            f"**Liczba epok:** {cfg['epochs']}  \n"
            f"**Populacja:** {cfg['population']}  \n"
            f"**Selekcja:** {SELECTION_METHODS[sel['method']]}"
            + (f" (rozmiar turnieju {sel['tournament_size']})" if sel["method"]== "tournament" else "")
            + (f" ({sel[sel['method']+'_percent']}%)" if sel["method"] in ("best", "worst") else "")
            + f"  \n**Krzyżowanie:** {CROSSOVER_METHODS[cx['method']]} | p={cx['probability']}  \n"
            + f"**Mutacja:** {MUTATION_METHODS[mut['method']]} | p={mut['probability']}  \n"
            + f"**Inwersja:** {'włączona' if cfg['inversion']['enabled'] else 'wyłączona'}"
            + (f" | p={cfg['inversion']['probability']}" if cfg['inversion']['enabled'] else "")
            + f"  \n**Elityzm:** {'włączony' if cfg['elitism']['enabled'] else 'wyłączony'}"
            + (f" | {cfg['elitism']['rate'] * 100:g}%" if cfg['elitism']['enabled'] else "")
        )

    st.checkbox("Zapisuj do bazy wszystkich osobników z każdej epoki (bardzo zwiększa rozmiar bazy)", key="save_individuals")
    col1, col2= st.columns(2)
    col1.button("Konfiguracja", width="stretch", on_click=open_config)
    if col2.button("Wykonaj", type="primary", width="stretch"):
        try: 
            ga_config=to_ga_config(cfg)
            with st.spinner("myślenie..."):
                rec=run_with_recording(ga_config, save_individuals=st.session_state.get("save_individuals", False))
            st.session_state["simulation"]=rec.sim
            st.session_state["simulation_time"]=rec.compute_time
            st.session_state["run_id"]=rec.run_id
        except Exception as e: st.exception(e)
        #except ValueError as e: st.error(f"Error config: {e}")
    if "simulation" in st.session_state:
        s = st.session_state["simulation"]

        best= (min(s.history, key=lambda stat: stat.best_fitness)if s.config.goal == "min" else max(s.history, key=lambda stat: stat.best_fitness))
        st.subheader("Wyniki")
        st.metric("Najlepsza otrzyman wartość:", f"{best.best_fitness:.6f}")
        st.metric("Czas obliczeń:", f"{st.session_state['simulation_time']:.2f} s")
        st.write("Najlepsze rozwiązanie:",", ".join(f"x{i} = {x:.6f}" for i, x in enumerate(best.best_x, start=1)))
        st.write("Najlepszy wynik w epoce:", best.epoch)
        st.write("Łączna liczba epok:", s.epoch)
        st.caption(f"Zapisano w bazie jako run_id={st.session_state['run_id']} ({DEFAULT_DB_PATH})")

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