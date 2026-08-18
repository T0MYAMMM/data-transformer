"""Tab 2: Script editor with example/saved script selection."""

import pandas as pd
import streamlit as st

from config import SessionKeys
from scripts import (
    EXAMPLE_SCRIPTS,
    ExecutionResult,
    Script,
    delete_script,
    execute_script,
    load_saved_scripts,
    save_script,
)


def init_state() -> None:
    """Initialize session state for the editor tab."""
    if SessionKeys.SCRIPT_CODE not in st.session_state:
        st.session_state[SessionKeys.SCRIPT_CODE] = ""


def render(tab) -> None:
    """Render the script editor tab."""
    with tab:
        st.subheader("Transformation Script")
        left_col, right_col = st.columns([1, 2])

        with left_col:
            _render_script_sidebar()

        with right_col:
            _render_editor()


def _render_script_sidebar() -> None:
    """Render example and saved script buttons."""
    st.markdown("**Example Scripts**")
    for script in EXAMPLE_SCRIPTS:
        if st.button(
            script.name, key=f"example_{script.name}", use_container_width=True
        ):
            _load_script(script.code)

    st.divider()
    saved = load_saved_scripts()
    if saved:
        st.markdown("**Saved Scripts**")
        for script in saved:
            btn_col, del_col = st.columns([4, 1])
            with btn_col:
                if st.button(
                    script.name,
                    key=f"saved_{script.name}",
                    use_container_width=True,
                ):
                    _load_script(script.code)
            with del_col:
                if st.button("X", key=f"del_{script.name}"):
                    delete_script(script.name)
                    st.rerun()


def _load_script(code: str) -> None:
    """Load a script into the editor and rerun."""
    st.session_state[SessionKeys.SCRIPT_CODE] = code
    st.session_state["code_editor_area"] = code
    st.rerun()


def _render_editor() -> None:
    """Render the code editor, run button, and save controls."""
    st.markdown("**Script Editor**")
    st.caption(
        "Use `df1` for Dataset 1, `df2` for Dataset 2. "
        "Libraries: `pd` (pandas), `np` (numpy), `pl` (polars), `json`, `re`. "
        "Assign output to `result`."
    )

    code = st.text_area(
        "Python script",
        value=st.session_state[SessionKeys.SCRIPT_CODE],
        height=300,
        key="code_editor_area",
        placeholder=(
            "# Available: df1, df2, pd, np, pl, json, re\n"
            "# Assign your output to 'result':\n"
            "#   result = df1[df1['column'] > 100]\n"
        ),
    )
    st.session_state[SessionKeys.SCRIPT_CODE] = code

    col_run, col_save = st.columns([1, 1])

    with col_run:
        if st.button("Run Script", type="primary", use_container_width=True):
            _run_script(code)

    with col_save:
        _render_save_controls(code)


def _run_script(code: str) -> None:
    """Execute the script and store results in session state."""
    df1 = st.session_state.get(SessionKeys.DF1)
    df2 = st.session_state.get(SessionKeys.DF2)

    if df1 is None:
        st.error("Load Dataset 1 in the Data Input tab first.")
        return
    if not code.strip():
        st.warning("Write a script before running.")
        return

    with st.spinner("Running script..."):
        result = execute_script(code, df1, df2)

    if not result.success:
        st.error(f"Script error: {result.error_message}")
        with st.expander("Full error details"):
            st.code(result.error_traceback)
        return

    if result.result is not None and isinstance(result.result, pd.DataFrame):
        st.session_state[SessionKeys.RESULT_DF] = result.result
        st.session_state[SessionKeys.RESULT_RAW] = None
        rows, cols = len(result.result), len(result.result.columns)
        st.success(f"Done. {rows} rows x {cols} columns")
        st.dataframe(result.result, use_container_width=True, height=300)
    elif result.result is not None:
        st.session_state[SessionKeys.RESULT_DF] = None
        st.session_state[SessionKeys.RESULT_RAW] = result.result
        st.info("Script returned a non-DataFrame result:")
        st.write(result.result)
    else:
        st.session_state[SessionKeys.RESULT_DF] = None
        st.session_state[SessionKeys.RESULT_RAW] = None
        st.warning("No result. Assign your output to `result`.")


def _render_save_controls(code: str) -> None:
    """Render the save-script expander."""
    with st.expander("Save Script"):
        save_name = st.text_input("Script name", key="save_name")
        save_desc = st.text_input("Description (optional)", key="save_desc")
        if st.button("Save", use_container_width=True):
            if save_name and code.strip():
                save_script(
                    Script(name=save_name, code=code, description=save_desc)
                )
                st.success(f"Script '{save_name}' saved.")
                st.rerun()
            else:
                st.warning("Enter a script name and code first.")
