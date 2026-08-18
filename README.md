# Data Transformer

A web-based data transformation tool for data engineers. Load tabular data, apply Python transformation scripts, and export results -- all from the browser.

## Features

- **Multiple input formats** -- paste or upload CSV, TSV, Excel (XLSX/XLS), JSON, or whitespace-delimited data. The parser auto-detects the format.
- **Dual dataset support** -- load two datasets at once for comparisons, merges, and diffs.
- **Built-in example scripts** -- 7 ready-to-use templates (find missing rows, merge, filter, deduplicate, diff, column ops, group-by).
- **Custom script editor** -- write and run arbitrary Python code with multiple libraries available.
- **Save and load scripts** -- persist custom scripts as JSON files for reuse across sessions.
- **Multi-format export** -- download results as CSV, TSV, JSON, or Excel.
- **Data summary** -- view column types and descriptive statistics for any result.

## Requirements

- Python >= 3.12
- [Poetry](https://python-poetry.org/) for dependency management

## Setup

```bash
cd data-transformer

# Install dependencies
poetry install

# Run the app
poetry run streamlit run app.py
```

The app starts at `http://localhost:5000` by default (see `.streamlit/config.toml`).

## Usage

### Workflow

1. **Data Input** tab -- paste or upload one or two datasets.
2. **Script Editor** tab -- pick an example script or write your own.
3. **Results** tab -- view the output and download in your preferred format.

### Writing Scripts

Scripts run in an isolated Python namespace with the following variables:

| Variable | Type / Library | Description |
|----------|---------------|-------------|
| `df1`    | `pd.DataFrame` | Dataset 1 (always available) |
| `df2`    | `pd.DataFrame` or `None` | Dataset 2 (optional) |
| `pd`     | pandas | `import pandas as pd` |
| `np`     | numpy | `import numpy as np` |
| `pl`     | polars | `import polars as pl` |
| `json`   | json | Python standard library |
| `re`     | re | Python standard library |

Assign your output to `result`:

```python
# Example: filter rows where the first column has no nulls
column_name = df1.columns[0]
result = df1[df1[column_name].notna()]
```

```python
# Example: convert a pandas DataFrame to polars, transform, and convert back
pldf = pl.from_pandas(df1)
result = pldf.filter(pl.col("amount") > 100).to_pandas()
```

### Saving Scripts

In the Script Editor tab, click **Save Script**, enter a name, and save. Scripts persist as JSON files in `saved_scripts/` and appear in the sidebar on reload.

### Supported Data Formats

**Input (paste or upload):**

| Format | Paste | Upload |
|--------|-------|--------|
| CSV    | Yes   | `.csv` |
| TSV    | Yes   | `.tsv` |
| Excel  | --    | `.xlsx`, `.xls` |
| JSON   | Yes   | `.json` |
| Whitespace-delimited | Yes | `.txt` |
| Semicolon-delimited  | Yes | -- |

**Output (download):** CSV, TSV, JSON, Excel

## Project Structure

```
data-transformer/
├── app.py                  # Entry point (wires tabs together)
├── config.py               # Constants, paths, session-state keys
├── parsers.py              # Data loading: CSV, TSV, JSON, Excel
├── scripts.py              # Example scripts, CRUD, execution engine
├── ui/
│   ├── __init__.py
│   ├── input_tab.py        # Tab 1: data input
│   ├── editor_tab.py       # Tab 2: script editor
│   └── results_tab.py      # Tab 3: results and export
├── saved_scripts/          # User-saved scripts (JSON)
├── .streamlit/
│   └── config.toml         # Server configuration
├── pyproject.toml           # Dependencies (Poetry)
└── README.md
```

### Architecture

The app follows a simple layered structure:

- **`config.py`** -- all constants and configuration in one place. Add new file types, libraries, or session keys here.
- **`parsers.py`** -- pure data-loading functions. No Streamlit UI logic (except `st.error` for file-upload failures).
- **`scripts.py`** -- script storage (load/save/delete JSON files), built-in example scripts, and the `exec()`-based execution engine. To add a new library to the script runtime, add it to `SCRIPT_LIBRARIES` in `config.py`.
- **`ui/`** -- each tab is a self-contained module with `init_state()` and `render(tab)`. UI code only; business logic lives in `parsers.py` and `scripts.py`.
- **`app.py`** -- thin entry point that initializes state and delegates to the three tab modules.

### Adding a New Example Script

Edit `scripts.py` and append a `Script(...)` to the `EXAMPLE_SCRIPTS` list:

```python
Script(
    name="My New Script",
    description="What this script does.",
    code="result = df1.head(10)\n",
)
```

### Adding a New Library

1. Add the library to `pyproject.toml` dependencies.
2. Add a mapping in `config.py` under `SCRIPT_LIBRARIES`:
   ```python
   SCRIPT_LIBRARIES = {
       ...
       "alias": "module_name",
   }
   ```
3. Update the caption in `ui/editor_tab.py` to mention the new alias.

## Configuration

Server settings in `.streamlit/config.toml`:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

Override the port with: `streamlit run app.py --server.port 8501`
