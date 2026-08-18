"""Script storage, example scripts, and execution engine."""

import importlib
import json
import os
import traceback
from dataclasses import dataclass, field
from typing import Any, Optional

import pandas as pd

from config import SCRIPTS_DIR, SCRIPT_LIBRARIES


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Script:
    """A transformation script with metadata."""

    name: str
    code: str
    description: str = ""


@dataclass
class ExecutionResult:
    """Result of running a transformation script."""

    success: bool
    result: Any = None
    error_message: str = ""
    error_traceback: str = ""


# ---------------------------------------------------------------------------
# Built-in example scripts
# ---------------------------------------------------------------------------

EXAMPLE_SCRIPTS: list[Script] = [
    Script(
        name="Find Missing Rows (by key column)",
        description="Find rows in Dataset 1 that are missing from Dataset 2, based on a key column.",
        code=(
            "# Find missing rows based on a key column\n"
            "# Uses the first column as the key by default\n"
            "\n"
            "key_column = df1.columns[0]  # e.g. 'cust_cd'\n"
            "\n"
            "missing = df1[~df1[key_column].isin(df2[key_column])]\n"
            "\n"
            "result = missing\n"
        ),
    ),
    Script(
        name="Merge / Join Two Datasets",
        description="Join two datasets on a common column (inner, left, right, or outer join).",
        code=(
            "# Merge two datasets on a common key column\n"
            "key_column = df1.columns[0]\n"
            "join_type = 'inner'  # Options: 'inner', 'left', 'right', 'outer'\n"
            "\n"
            "result = pd.merge(df1, df2, on=key_column, how=join_type, suffixes=('_old', '_new'))\n"
        ),
    ),
    Script(
        name="Filter Rows by Condition",
        description="Filter rows where a column meets a condition.",
        code=(
            "# Filter rows where a column meets a condition\n"
            "column_name = df1.columns[0]\n"
            "\n"
            "# Examples:\n"
            "# result = df1[df1[column_name] > 100]\n"
            "# result = df1[df1[column_name] == 'some_value']\n"
            "# result = df1[df1[column_name].str.contains('search_term', na=False)]\n"
            "\n"
            "result = df1[df1[column_name].notna()]\n"
        ),
    ),
    Script(
        name="Remove Duplicate Rows",
        description="Remove duplicate rows based on selected columns or all columns.",
        code=(
            "# Remove duplicates from dataset\n"
            "subset = None  # e.g. ['cust_cd', 'cust_nm'] or None for all\n"
            "keep = 'first'  # Options: 'first', 'last', False (drop all duplicates)\n"
            "\n"
            "result = df1.drop_duplicates(subset=subset, keep=keep)\n"
        ),
    ),
    Script(
        name="Compare Two Datasets (Diff)",
        description="Show differences between two datasets side by side.",
        code=(
            "# Compare two datasets and show differences\n"
            "key_column = df1.columns[0]\n"
            "\n"
            "merged = pd.merge(df1, df2, on=key_column, how='outer',\n"
            "                  indicator=True, suffixes=('_old', '_new'))\n"
            "\n"
            "merged['status'] = merged['_merge'].map({\n"
            "    'left_only': 'Only in Dataset 1',\n"
            "    'right_only': 'Only in Dataset 2',\n"
            "    'both': 'In Both'\n"
            "})\n"
            "\n"
            "result = merged.drop(columns=['_merge'])\n"
        ),
    ),
    Script(
        name="Add / Rename / Drop Columns",
        description="Modify columns in a dataset.",
        code=(
            "# Column operations on df1\n"
            "\n"
            "# Rename columns\n"
            "# result = df1.rename(columns={'old_name': 'new_name'})\n"
            "\n"
            "# Drop columns\n"
            "# result = df1.drop(columns=['column_to_drop'])\n"
            "\n"
            "# Add a new column\n"
            "# df1['new_column'] = df1['existing_column'].apply(lambda x: x * 2)\n"
            "\n"
            "result = df1.copy()\n"
        ),
    ),
    Script(
        name="Aggregate / Group By",
        description="Group data and compute aggregations (sum, count, mean, etc.).",
        code=(
            "# Group by a column and aggregate\n"
            "group_column = df1.columns[0]\n"
            "\n"
            "result = df1.groupby(group_column).agg('count').reset_index()\n"
            "# Other options: 'sum', 'mean', 'min', 'max', 'first', 'last'\n"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Saved scripts (JSON persistence)
# ---------------------------------------------------------------------------

def load_saved_scripts() -> list[Script]:
    """Load all user-saved scripts from the saved_scripts directory."""
    scripts = []
    for fname in sorted(os.listdir(SCRIPTS_DIR)):
        if not fname.endswith(".json"):
            continue
        try:
            with open(SCRIPTS_DIR / fname) as f:
                data = json.load(f)
            scripts.append(Script(
                name=data["name"],
                code=data["code"],
                description=data.get("description", ""),
            ))
        except Exception:
            continue
    return scripts


def save_script(script: Script) -> None:
    """Save a script to disk as JSON (backward-compatible format)."""
    safe_name = "".join(
        c if c.isalnum() or c in "-_ " else "" for c in script.name
    ).strip()
    fname = safe_name.replace(" ", "_") + ".json"
    with open(SCRIPTS_DIR / fname, "w") as f:
        json.dump(
            {"name": script.name, "description": script.description, "code": script.code},
            f,
            indent=2,
        )


def delete_script(name: str) -> bool:
    """Delete a saved script by name. Returns True if found and deleted."""
    for fname in os.listdir(SCRIPTS_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(SCRIPTS_DIR / fname) as f:
                data = json.load(f)
            if data["name"] == name:
                os.remove(SCRIPTS_DIR / fname)
                return True
        except Exception:
            continue
    return False


# ---------------------------------------------------------------------------
# Execution engine
# ---------------------------------------------------------------------------

def _build_exec_context(
    df1: pd.DataFrame, df2: Optional[pd.DataFrame] = None
) -> dict:
    """Build the namespace for script execution.

    Includes df1, df2, pandas, and any additional libraries listed in
    config.SCRIPT_LIBRARIES that are installed.
    """
    context: dict[str, Any] = {
        "df1": df1,
        "df2": df2,
        "result": None,
    }
    for alias, module_name in SCRIPT_LIBRARIES.items():
        try:
            context[alias] = importlib.import_module(module_name)
        except ImportError:
            pass  # library not installed -- skip silently
    return context


def execute_script(
    code: str,
    df1: pd.DataFrame,
    df2: Optional[pd.DataFrame] = None,
) -> ExecutionResult:
    """Execute a transformation script in an isolated namespace.

    The script should assign its output to the variable ``result``.
    Available variables depend on config.SCRIPT_LIBRARIES.
    """
    context = _build_exec_context(
        df1.copy(),
        df2.copy() if df2 is not None else None,
    )
    try:
        exec(code, {"__builtins__": __builtins__}, context)
        return ExecutionResult(success=True, result=context.get("result"))
    except Exception as e:
        return ExecutionResult(
            success=False,
            error_message=str(e),
            error_traceback=traceback.format_exc(),
        )
