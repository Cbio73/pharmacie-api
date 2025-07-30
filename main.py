from fastapi import FastAPI
import sqlite3
import os
import pandas as pd

app = FastAPI()

DB_FILE = "pharmacie.db"
CSV_FILE = "pharmacies_et_dieteticiens_filtrés.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        print("Création de la base de données...")
        df = pd.read_csv(CSV_FILE, sep=",", dtype=str)
        conn = sqlite3.connect(DB_FILE)
        df.to_sql("professionnels", conn, if_exists="replace", index=False)
        conn.close()
        print("Base créée avec succès.")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return {"message": "API pharmacie opérationnelle"}

@app.get("/pharmacies")
def get_pharmacies(departement: str):
    conn = sqlite3.connect(DB_FILE)
    query = '''
        SELECT 
            "Numéro FINESS site" AS finess,
            "Raison sociale site" AS nom_pharmacie,
            "Code postal (coord. structure)" AS code_postal,
            "Libellé commune (coord. structure)" AS commune,
            COUNT(*) AS nombre_professionnels
        FROM professionnels
        WHERE substr("Code postal (coord. structure)", 1, 2) = ?
        GROUP BY "Numéro FINESS site", "Raison sociale site", "Code postal (coord. structure)", "Libellé commune (coord. structure)"
        ORDER BY nom_pharmacie
    '''
    df = pd.read_sql_query(query, conn, params=(departement,))
    return df.to_dict(orient="records")