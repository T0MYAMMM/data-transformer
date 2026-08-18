"""Application configuration and constants."""

from pathlib import Path

# Paths
APP_DIR = Path(__file__).parent
SCRIPTS_DIR = APP_DIR / "saved_scripts"
SCRIPTS_DIR.mkdir(exist_ok=True)

# Page
PAGE_TITLE = "Data Transformer"
PAGE_LAYOUT = "wide"

# Supported file types for upload
UPLOAD_FILE_TYPES = ["csv", "tsv", "txt", "xlsx", "xls", "json"]

# Libraries available in the script execution context.
# Keys are the variable names exposed to user scripts;
# values are the Python module names to import.
SCRIPT_LIBRARIES = {
    "pd": "pandas",
    "np": "numpy",
    "pl": "polars",
    "json": "json",
    "re": "re",
}


class SessionKeys:
    """Centralized session-state key names to avoid typos."""

    DF1 = "df1"
    DF2 = "df2"
    SCRIPT_CODE = "script_code"
    RESULT_DF = "result_df"
    RESULT_RAW = "result_raw"
