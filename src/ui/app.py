import copy

import streamlit as st

from src.ui.constants import DEFAULT_CONFIG
from src.ui.config_screen import render_config_screen
from src.ui.main_screen import render_main_screen


SCREENS= {
    "main": render_main_screen,
    "config": render_config_screen,
}


def init_state():
    st.session_state.setdefault("screen", "main")
    st.session_state.setdefault("ga_config", copy.deepcopy(DEFAULT_CONFIG))
    st.session_state.setdefault("config_errors", [])


st.set_page_config(page_title="Algorytm genetyczny", layout="centered")
init_state()
SCREENS[st.session_state.screen]()
