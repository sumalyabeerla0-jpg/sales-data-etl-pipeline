import pandas as pd
from src.pipeline import transform

def test_transform_accepts_valid_and_rejects_invalid_rows():
    raw = pd.DataFrame([
        {"order_id":"1","customer_id":"C1","order_date":"2026-01-01","product":"Pen","category":"Stationery","quantity":"2","unit_price":"10"},
        {"order_id":"2","customer_id":"","order_date":"2026-01-01","product":"Book","category":"Books","quantity":"1","unit_price":"20"},
    ])
    clean, rejected, metrics = transform(raw)
    assert len(clean) == 1
    assert clean.iloc[0]["revenue"] == 20
    assert len(rejected) == 1
    assert metrics["accepted_rows"] == 1
