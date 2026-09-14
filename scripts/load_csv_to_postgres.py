#!/usr/bin/env python3
"""Loads every CSV in data/ into postgres as a table (all columns TEXT).

Table name = filename with the leading hash prefix and .csv extension stripped,
e.g. data/2c6zaeunjgb6-jaffle_shop_orders.csv -> table "jaffle_shop_orders".

Connects directly to the postgres container via its published host port
(matches the "dev" target in profiles.yml), so it can be run from the host
without going through docker exec.
"""
import csv
import glob
import os
import re
import sys

import psycopg2

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

DB_PARAMS = dict(
    host=os.environ.get("PGHOST", "localhost"),
    port=os.environ.get("PGPORT", "5434"),
    user=os.environ.get("PGUSER", "admin"),
    password=os.environ.get("PGPASSWORD", "admin123"),
    dbname=os.environ.get("PGDATABASE", "raw"),
)

SCHEMA = os.environ.get("PGSCHEMA", "jaffle_shop")

# (schema, table) overrides for specific source tables, keyed by the
# filename-derived table name.
TABLE_OVERRIDES = {
    "stripe_payments": ("stripe", "payment"),
}


def table_name_for(csv_path):
    filename = os.path.basename(csv_path)
    stem = re.sub(r"^[a-z0-9]+-", "", filename)
    stem = re.sub(r"\.csv$", "", stem)
    return stem


def target_for(csv_path):
    table = table_name_for(csv_path)
    return TABLE_OVERRIDES.get(table, (SCHEMA, table))


def sanitize_column(name):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip()).strip("_").lower()
    return name or "col"


def load_csv(cur, csv_path):
    schema, table = target_for(csv_path)

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f))
    columns = [sanitize_column(col) for col in header]

    print(f"Loading {os.path.basename(csv_path)} -> table \"{schema}\".\"{table}\" ({len(columns)} columns)")

    cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
    cur.execute(f'DROP TABLE IF EXISTS "{schema}"."{table}" CASCADE')
    col_defs = ", ".join(f'"{col}" TEXT' for col in columns)
    cur.execute(f'CREATE TABLE "{schema}"."{table}" ({col_defs})')

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        cur.copy_expert(
            f'COPY "{schema}"."{table}" FROM STDIN WITH (FORMAT csv, HEADER true)', f
        )

    return schema, table


def main():
    csv_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(**DB_PARAMS)
    conn.autocommit = False
    try:
        targets = []
        with conn.cursor() as cur:
            for csv_path in csv_files:
                targets.append(load_csv(cur, csv_path))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("\nDone. Row counts:")
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        with conn.cursor() as cur:
            for schema, table in targets:
                cur.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
                count = cur.fetchone()[0]
                print(f"  {schema}.{table}: {count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
