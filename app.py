"""CapAssigner - Capacitor Network Synthesis Application.

Streamlit entry point for the application.
"""

import streamlit as st
from capassigner.ui.pages import render_main_page


st.set_page_config(
    page_title="CapAssigner",
    page_icon="🔌",
    layout="wide",
)

render_main_page()
