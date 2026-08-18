# Data Transformer

## Overview
A Streamlit web application for data transformation. Users can paste or upload tabular data (from Excel, CSV, etc.), apply custom Python transformation scripts, and download the results.

## Architecture
- **Framework**: Streamlit (Python)
- **Data Processing**: pandas
- **Port**: 5000 (configured in .streamlit/config.toml)

## Key Features
- Paste data from Excel/CSV or upload files (CSV, TSV, TXT, XLSX)
- Auto-detect delimiter (tab, comma, semicolon)
- Support for two datasets (for comparison/merge operations)
- Built-in example transformation scripts
- Custom script editor with save/load functionality
- Download results as CSV, TSV, or Excel

## File Structure
- `app.py` - Main Streamlit application
- `saved_scripts/` - Directory for user-saved transformation scripts (JSON)
- `.streamlit/config.toml` - Streamlit server configuration

## Running
```
streamlit run app.py --server.port 5000
```
