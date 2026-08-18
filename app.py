"""Data Transformer -- entry point.

A utility for data engineers to quickly load, transform, and export tabular data.
Run with: streamlit run app.py
"""

import streamlit as st

from config import PAGE_LAYOUT, PAGE_TITLE
from ui import editor_tab, input_tab, results_tab

st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)

# Initialize all session state before any widget is created.
input_tab.init_state()
editor_tab.init_state()
results_tab.init_state()

st.title("Data Transformer")
st.caption("Load data, apply transformation scripts, export results.")

tab_input, tab_script, tab_result = st.tabs(
    ["1. Data Input", "2. Script Editor", "3. Results"]
)

input_tab.render(tab_input)
editor_tab.render(tab_script)
results_tab.render(tab_result)
