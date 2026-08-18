"""Data parsing for multiple formats.

Supports CSV, TSV, semicolon-delimited, whitespace-delimited, JSON, and Excel.
"""

import io
import json
from typing import Optional

import pandas as pd
import streamlit as st


def parse_text(text: str) -> Optional[pd.DataFrame]:
    """Auto-detect format and parse pasted text into a DataFrame.

    Tries formats in order: JSON array/object, TSV, CSV, semicolon-separated,
    whitespace-separated, then single-column CSV as a fallback.
    Returns None if all attempts fail.
    """
    text = text.strip()
    if not text:
        return None

    # JSON (array of objects, or column-oriented dict)
    df = _try_json(text)
    if df is not None:
        return df

    # Delimited formats -- require more than one column to be considered valid
    for sep in ("\t", ",", ";"):
        df = _try_delimited(text, sep)
        if df is not None and len(df.columns) > 1:
            return df

    # Whitespace-delimited
    df = _try_delimited(text, r"\s+")
    if df is not None and len(df.columns) > 1:
        return df

    # Fallback: single-column CSV
    try:
        return pd.read_csv(io.StringIO(text))
    except Exception:
        return None


def parse_file(uploaded_file) -> Optional[pd.DataFrame]:
    """Parse an uploaded file into a DataFrame.

    Supports CSV, TSV, TXT, XLSX, XLS, and JSON.
    """
    name = uploaded_file.name.lower()
    try:
        if name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        if name.endswith(".tsv"):
            return pd.read_csv(uploaded_file, sep="\t")
        if name.endswith(".json"):
            return pd.read_json(uploaded_file)
        # Default: CSV / TXT
        return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _try_json(text: str) -> Optional[pd.DataFrame]:
    """Attempt to parse text as a JSON array or object."""
    try:
        data = json.loads(text)
        if isinstance(data, list) and len(data) > 0:
            return pd.DataFrame(data)
        if isinstance(data, dict):
            # Column-oriented: {"col1": [...], "col2": [...]}
            if all(isinstance(v, list) for v in data.values()):
                return pd.DataFrame(data)
            # Single object -> one-row DataFrame
            return pd.DataFrame([data])
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _try_delimited(text: str, sep: str) -> Optional[pd.DataFrame]:
    """Attempt to parse text with a specific delimiter."""
    try:
        return pd.read_csv(io.StringIO(text), sep=sep)
    except Exception:
        return None
