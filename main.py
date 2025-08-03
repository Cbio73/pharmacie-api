from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd

app = FastAPI()

# Middleware CORS pour autoriser le frontend React local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion à la base de données SQLite
conn = sqlite3.connect("pharmacie.db", check_same_thread=False)

@app.get("/")
def read_root():
    return {"message": "API pharmacie opérationnelle"}

@app.get("/pharmacies")
def get_pharmacies(
    departement: str = Query(..., description="Code du département"),
    ville: str = Query(None, description="Nom de la ville (facultatif)"),
    tri: str = Query("pharmaciens", description="Critère de tri : 'pharmaciens' (par défaut)")
):
    base_query = """
        SELECT finess, nom_pharmacie, code_postal, commune, COUNT(*) AS nombre_professionnels
        FROM professionnels
        WHERE code_postal LIKE ? AND profession = 'Pharmacien'
    """

    params = [f"{departement}%"]

    if ville:
        base_query += " AND LOWER(commune) = LOWER(?)"
        params.append(ville)

    base_query += " GROUP BY finess ORDER BY nombre_professionnels DESC"

    df = pd.read_sql_query(base_query, conn, params=params)

    return df.to_dict(orient="records")
