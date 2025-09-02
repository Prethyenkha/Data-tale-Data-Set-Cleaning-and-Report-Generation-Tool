import re
import pandas as pd
import numpy as np
from datetime import datetime

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def clean_dataframe(df: pd.DataFrame):
    audit = {
        "rows_before": len(df),
        "rows_after": None,
        "duplicates_removed": 0,
        "columns": list(df.columns),
        "column_changes": {col: {} for col in df.columns},
        "issues": []
    }

    # 1) Trim whitespace for object columns
    for col in df.select_dtypes(include=["object"]).columns:
        before_nulls = df[col].isna().sum()
        df[col] = df[col].astype(str).str.strip()
        # Fix: Use loc to avoid chained assignment warning
        df.loc[df[col] == "", col] = pd.NA
        after_nulls = df[col].isna().sum()
        delta = after_nulls - before_nulls
        if delta != 0:
            audit["column_changes"][col]["new_nulls_from_empty_strings"] = int(delta)

    # 2) Parse dates when column name hints or parseable ratio is high
    for col in df.columns:
        cl = col.lower()
        if ("date" in cl) or ("_at" in cl) or ("time" in cl):
            parsed = pd.to_datetime(df[col], errors="coerce", utc=True)
            converted = parsed.notna().sum()
            if converted > 0:
                df[col] = parsed.dt.tz_convert(None)
                audit["column_changes"][col]["parsed_to_datetime"] = int(converted)

    # 3) Normalize emails
    for col in df.select_dtypes(include=["object"]).columns:
        if "email" in col.lower():
            before_valid = df[col].apply(lambda x: bool(EMAIL_RE.match(str(x))) if pd.notna(x) else False).sum()
            df[col] = df[col].str.lower()
            after_valid = df[col].apply(lambda x: bool(EMAIL_RE.match(str(x))) if pd.notna(x) else False).sum()
            audit["column_changes"][col]["emails_valid_before"] = int(before_valid)
            audit["column_changes"][col]["emails_valid_after"] = int(after_valid)

    # 4) Remove duplicates (normalized string compare on object cols)
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    norm = df.copy()
    for c in obj_cols:
        norm[c] = norm[c].str.lower().str.strip()
    before = len(df)
    df = df.loc[~norm.duplicated(), :].copy()
    removed = before - len(df)
    if removed > 0:
        audit["duplicates_removed"] = int(removed)

    # 5) Impute missing values by dtype
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            val = float(df[col].median()) if df[col].notna().any() else 0.0
            # Fix: Use loc to avoid chained assignment warning
            df.loc[df[col].isna(), col] = val
            audit["column_changes"][col]["imputed_missing"] = int(missing_count)
            audit["column_changes"][col]["imputation_strategy"] = f"median={val}"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            mode = df[col].mode(dropna=True)
            val = mode.iloc[0] if not mode.empty else pd.NaT
            # Fix: Use loc to avoid chained assignment warning
            df.loc[df[col].isna(), col] = val
            audit["column_changes"][col]["imputed_missing"] = int(missing_count)
            audit["column_changes"][col]["imputation_strategy"] = "mode (datetime)"
        else:
            mode = df[col].mode(dropna=True)
            val = mode.iloc[0] if not mode.empty else "Unknown"
            # Fix: Use loc to avoid chained assignment warning
            df.loc[df[col].isna(), col] = val
            audit["column_changes"][col]["imputed_missing"] = int(missing_count)
            audit["column_changes"][col]["imputation_strategy"] = f"mode='{val}'"

    audit["rows_after"] = int(len(df))
    return df, audit

def build_audit_summary(audit: dict) -> dict:
    summary = {
        "rows_before": audit["rows_before"],
        "rows_after": audit["rows_after"],
        "duplicates_removed": audit.get("duplicates_removed", 0),
        "columns": audit["columns"],
        "column_changes": {},
        "issues": audit.get("issues", []),
    }
    for col, info in audit["column_changes"].items():
        pretty = {}
        for k, v in info.items():
            pretty[k] = v
        summary["column_changes"][col] = pretty
    return summary
