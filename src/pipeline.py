"""Small, reproducible CSV -> transform -> SQLite ETL pipeline."""
from pathlib import Path
import argparse
import sqlite3
import pandas as pd

REQUIRED = ["order_id", "customer_id", "order_date", "product", "category", "quantity", "unit_price"]

def extract(csv_path: str) -> pd.DataFrame:
    """Read raw CSV data as strings so validation is explicit."""
    return pd.read_csv(csv_path, dtype=str)

def transform(df: pd.DataFrame):
    """Normalize, validate and calculate order revenue.

    Returns (clean_dataframe, rejected_dataframe, metrics).
    Duplicate order IDs, missing customer IDs, invalid dates, non-positive
    quantities and negative prices are rejected rather than silently fixed.
    """
    work = df.copy()
    missing_cols = [c for c in REQUIRED if c not in work.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    for col in ["order_id", "customer_id", "product", "category"]:
        work[col] = work[col].astype("string").str.strip()

    work["order_date"] = pd.to_datetime(work["order_date"], errors="coerce", dayfirst=True, format="mixed")
    work["quantity"] = pd.to_numeric(work["quantity"], errors="coerce")
    work["unit_price"] = pd.to_numeric(work["unit_price"], errors="coerce")

    reasons = pd.Series("", index=work.index, dtype="string")
    def flag(mask, reason):
        nonlocal reasons
        reasons = reasons.mask(mask & reasons.eq(""), reason)
        reasons = reasons.mask(mask & reasons.ne(reason), reasons + ";" + reason)

    flag(work["order_id"].isna() | work["order_id"].eq(""), "missing_order_id")
    flag(work["customer_id"].isna() | work["customer_id"].eq(""), "missing_customer_id")
    flag(work["order_date"].isna(), "invalid_order_date")
    flag(work["quantity"].isna() | (work["quantity"] <= 0), "invalid_quantity")
    flag(work["unit_price"].isna() | (work["unit_price"] < 0), "invalid_unit_price")

    duplicated = work["order_id"].duplicated(keep="first") & work["order_id"].notna()
    flag(duplicated, "duplicate_order_id")

    rejected = work[reasons.ne("")].copy()
    rejected["rejection_reason"] = reasons[reasons.ne("")]
    clean = work[reasons.eq("")].copy()
    clean["revenue"] = clean["quantity"] * clean["unit_price"]
    clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")
    metrics = {
        "input_rows": int(len(df)),
        "accepted_rows": int(len(clean)),
        "rejected_rows": int(len(rejected)),
        "revenue_total": float(clean["revenue"].sum()) if len(clean) else 0.0,
    }
    return clean, rejected, metrics

def load(clean: pd.DataFrame, rejected: pd.DataFrame, db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        clean.to_sql("sales", conn, if_exists="replace", index=False)
        rejected.to_sql("rejected_sales", conn, if_exists="replace", index=False)

def run(input_path: str, db_path: str, output_dir: str):
    df = extract(input_path)
    clean, rejected, metrics = transform(df)
    load(clean, rejected, db_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out / "clean_sales.csv", index=False)
    rejected.to_csv(out / "rejected_sales.csv", index=False)
    (out / "run_metrics.json").write_text(__import__("json").dumps(metrics, indent=2))
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the sales ETL pipeline")
    parser.add_argument("--input", default="data/raw_sales.csv")
    parser.add_argument("--db", default="output/sales.db")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()
    print(run(args.input, args.db, args.output))
