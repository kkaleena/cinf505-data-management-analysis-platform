import os
import re
import pandas as pd
from sqlalchemy import create_engine, text # engine = connection; text = raw SQL

# The SQLite file will be saves inside this folder
os.makedirs("data", exist_ok=True)
# Connect to the database. If the file does not exist --> create a new one
engine = create_engine("sqlite:///data/app.db")


def _table_name(name: str) -> str:
    # Make a safe table name from a dataset name
    # Clean the name string
    return "ds_" + re.sub(r"[^0-9a-zA-Z_]", "_", name)

def init_db():
    # create the catalog table id it doesn't exist
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS datasets ("
            "name TEXT PRIMARY KEY, upload_date TEXT)"))


def save_dataset(name: str, df: pd.DataFrame):
    # Save a dataset and register it in the catalog
    # If there is a table with the same name, user can overwrite it
    init_db()
    df.to_sql(_table_name(name), engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        # :n --> a bound parameter (safer to put the name into the SQL string)
        conn.execute(text("DELETE FROM datasets WHERE name = :n"), {"n": name})
        # add the current date and time
        conn.execute(text(
            "INSERT INTO datasets (name, upload_date) "
            "VALUES (:n, datetime('now'))"), {"n": name})

def list_datasets() -> list:
    # Return the names of all saved dataset, from new --> old file
    init_db()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT name FROM datasets ORDER BY upload_date DESC")).fetchall()
    return [r[0] for r in rows]


def load_dataset(name: str) -> pd.DataFrame:
    # Load a saved dataset back into a Pandas DataFrame
    # Use the same name-Cleaning rule as save_dataset
    return pd.read_sql_table(_table_name(name), engine)