from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd

app = FastAPI()

# Middleware CORS pour autoriser le frontend React local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    tri: str = Query("pharmaciens", description="Critère de tri (par défaut: pharmaciens)")
):
    query = """
        SELECT 
            "Numéro FINESS site" AS finess,
            "Raison sociale site" AS nom_pharmacie,
            "Code postal (coord. structure)" AS code_postal,
            "Libellé commune (coord. structure)" AS commune,
            COUNT(*) AS nombre_professionnels
        FROM professionnels
        WHERE "Code postal (coord. structure)" LIKE ? AND "Libellé profession" = 'Pharmacien'
    """

    params = [f"{departement}%"]

    if ville:
        query += " AND LOWER(\"Libellé commune (coord. structure)\") = LOWER(?)"
        params.append(ville)

    query += """
        GROUP BY "Numéro FINESS site"
        ORDER BY nombre_professionnels DESC
    """

    df = pd.read_sql_query(query, conn, params=params)
    return df.to_dict(orient="records")
