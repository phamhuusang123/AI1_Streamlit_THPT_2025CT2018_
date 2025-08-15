# src/data_loader.py
import os
import io

try:
    import polars as pl
    HAS_POLARS = True
except Exception:
    HAS_POLARS = False

import pandas as pd

def load_data(path: str, use_polars_if_possible: bool = True):
    """
    Load CSV/XLSX from a given path.
    Returns (df, backend) where backend is 'polars' or 'pandas'.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if HAS_POLARS and use_polars_if_possible and ext == ".csv":
        try:
            df = pl.read_csv(path)
            return df, "polars"
        except Exception:
            # fallback to pandas
            pass

    # pandas fallback (handles csv & xlsx)
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file extension")
    return df, "pandas"
