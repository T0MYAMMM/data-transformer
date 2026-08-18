"""Tab 1: Data input via paste or file upload."""

from typing import Optional

import pandas as pd
import streamlit as st

from config import UPLOAD_FILE_TYPES, SessionKeys
from parsers import parse_file, parse_text


def init_state() -> None:
    """Initialize session state for the input tab."""
    if SessionKeys.DF1 not in st.session_state:
        st.session_state[SessionKeys.DF1] = None
    if SessionKeys.DF2 not in st.session_state:
        st.session_state[SessionKeys.DF2] = None


def render(tab) -> None:
    """Render the data input tab."""
    with tab:
        input_method = st.radio(
            "Input method", ["Paste Data", "Upload File"], horizontal=True
        )
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dataset 1")
            df1 = _dataset_input(
                input_method,
                key_suffix="1",
                placeholder="Paste from Excel, CSV, JSON, or any tabular data...",
            )
            _show_preview(df1, input_method, key_suffix="1")
            st.session_state[SessionKeys.DF1] = df1

        with col2:
            st.subheader("Dataset 2 (optional)")
            df2 = _dataset_input(
                input_method,
                key_suffix="2",
                placeholder="Paste a second dataset for comparison/merge...",
            )
            _show_preview(df2, input_method, key_suffix="2")
            st.session_state[SessionKeys.DF2] = df2


def _dataset_input(
    method: str, key_suffix: str, placeholder: str
) -> Optional[pd.DataFrame]:
    """Render the input widget and return a parsed DataFrame (or None)."""
    if method == "Paste Data":
        text = st.text_area(
            "Paste data here (tab / comma / semicolon / JSON)",
            height=250,
            key=f"text{key_suffix}",
            placeholder=placeholder,
        )
        return parse_text(text) if text.strip() else None

    uploaded = st.file_uploader(
        "Upload file",
        type=UPLOAD_FILE_TYPES,
        key=f"file{key_suffix}",
    )
    return parse_file(uploaded) if uploaded else None


def _show_preview(
    df: Optional[pd.DataFrame], method: str, key_suffix: str
) -> None:
    """Show a data preview or a warning if parsing failed."""
    if df is not None:
        st.success(f"{len(df)} rows x {len(df.columns)} columns")
        st.dataframe(df, use_container_width=True, height=200)
    elif _has_input(method, key_suffix):
        st.warning("Could not parse the data. Check the format.")


def _has_input(method: str, key_suffix: str) -> bool:
    """Return True if the user has provided some input."""
    if method == "Paste Data":
        return bool(st.session_state.get(f"text{key_suffix}", "").strip())
    return st.session_state.get(f"file{key_suffix}") is not None
