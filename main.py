from fastapi import FastAPI
import sqlite3
import pandas as pd
import os

app = FastAPI()

@app.on_event("startup")
def startup_event():
    global conn
    db_path = os.path.join(os.path.dirname(__file__), "pharmacie.db")
    conn = sqlite3.connect(db_path)

@app.get("/pharmacies")
def get_pharmacies(departement: str, ville: str = None):
    base_query = """
        SELECT 
            "Numéro FINESS site" AS finess,
            "Raison sociale site" AS nom_pharmacie,
            "Code postal (coord. structure)" AS code_postal,
            "Libellé commune (coord. structure)" AS commune,
            COUNT(*) AS nombre_professionnels
        FROM professionnels
        WHERE substr("Code postal (coord. structure)", 1, 2) = ?
    """

    params = [departement]

    if ville:
        base_query += ' AND "Libellé commune (coord. structure)" = ?'
        params.append(ville)

    base_query += """
        GROUP BY "Numéro FINESS site", "Raison sociale site", "Code postal (coord. structure)", "Libellé commune (coord. structure)"
        ORDER BY nombre_professionnels DESC
    """

    df = pd.read_sql_query(base_query, conn, params=params)
    return df.to_dict(orient="records")
