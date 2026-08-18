"""Tab 3: Results display, export, and data summary."""

import io

import pandas as pd
import streamlit as st

from config import SessionKeys


def init_state() -> None:
    """Initialize session state for the results tab."""
    if SessionKeys.RESULT_DF not in st.session_state:
        st.session_state[SessionKeys.RESULT_DF] = None
    if SessionKeys.RESULT_RAW not in st.session_state:
        st.session_state[SessionKeys.RESULT_RAW] = None


def render(tab) -> None:
    """Render the results tab."""
    with tab:
        st.subheader("Results")
        result_df = st.session_state.get(SessionKeys.RESULT_DF)
        result_raw = st.session_state.get(SessionKeys.RESULT_RAW)

        if result_df is not None:
            _render_dataframe_result(result_df)
        elif result_raw is not None:
            st.info("Non-DataFrame result:")
            st.write(result_raw)
        else:
            st.info("No results yet. Load data and run a script to see results here.")


def _render_dataframe_result(df: pd.DataFrame) -> None:
    """Render a DataFrame result with export options and a summary."""
    st.success(f"Result: {len(df)} rows x {len(df.columns)} columns")
    st.dataframe(df, use_container_width=True, height=400)

    st.divider()
    _render_downloads(df)

    st.divider()
    _render_summary(df)


def _render_downloads(df: pd.DataFrame) -> None:
    """Render download buttons for CSV, TSV, JSON, and Excel."""
    st.markdown("**Download Result**")
    cols = st.columns(4)

    with cols[0]:
        st.download_button(
            "Download CSV",
            df.to_csv(index=False),
            "result.csv",
            "text/csv",
            use_container_width=True,
        )

    with cols[1]:
        st.download_button(
            "Download TSV",
            df.to_csv(index=False, sep="\t"),
            "result.tsv",
            "text/tab-separated-values",
            use_container_width=True,
        )

    with cols[2]:
        st.download_button(
            "Download JSON",
            df.to_json(orient="records", indent=2),
            "result.json",
            "application/json",
            use_container_width=True,
        )

    with cols[3]:
        try:
            buf = io.BytesIO()
            df.to_excel(buf, index=False, engine="openpyxl")
            buf.seek(0)
            st.download_button(
                "Download Excel",
                buf,
                "result.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except ImportError:
            st.info("Install openpyxl for Excel export.")


def _render_summary(df: pd.DataFrame) -> None:
    """Render column types and descriptive statistics."""
    st.markdown("**Data Summary**")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Column Types**")
        type_df = pd.DataFrame(
            {"Column": df.columns, "Type": df.dtypes.astype(str).values}
        )
        st.dataframe(type_df, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Statistics**")
        st.dataframe(df.describe(), use_container_width=True)
