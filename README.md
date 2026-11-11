# Project 1 — Sales ETL Pipeline

## What it does
Extracts raw sales rows from CSV, validates and transforms them with Pandas,
loads accepted and rejected records into SQLite, and writes run metrics.

## Stack
Python, Pandas, SQLite, SQL, pytest.

## Run
From this directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.pipeline
```

Outputs are created in `output/`: `sales.db`, clean/rejected CSVs and run metrics.
Run SQL examples using SQLite Browser or Python's sqlite3 module.

## Test
```bash
pip install pytest
pytest
```

## Design decisions
- Raw values are initially read as strings to make parsing and validation explicit.
- Invalid records are quarantined in `rejected_sales`, not silently discarded.
- The pipeline is repeatable: the current run replaces the target tables.
- SQLite keeps setup simple for a portfolio demonstration; a production version
  could use PostgreSQL or a cloud warehouse, incremental loads and orchestration.

## Interview talking points
Explain extraction, validation rules, rejected-row handling, idempotency of the
full-refresh load, and how you would scale this to large files (chunked reads,
staging tables, bulk loads, orchestration and monitoring).
