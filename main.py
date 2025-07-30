from fastapi import FastAPI, Query
import sqlite3
import pandas as pd

app = FastAPI()
DB_PATH = "pharmacie.db"

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Pharmacies de France"}

@app.get("/pharmacies")
def get_pharmacies(departement: str = Query(..., min_length=2, max_length=3)):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
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
    """
    df = pd.read_sql_query(query, conn, params=(departement,))
    conn.close()
    return df.to_dict(orient="records")

@app.get("/pharmacies/{finess}")
def get_pharmacie_by_finess(finess: str):
    conn = sqlite3.connect(DB_PATH)

    query_structure = """
        SELECT 
            "Numéro FINESS site" AS finess,
            "Raison sociale site" AS nom_pharmacie,
            "Enseigne commerciale site" AS enseigne,
            "Numéro Voie (coord. structure)" AS numero_voie,
            "Libellé type de voie (coord. structure)" AS type_voie,
            "Libellé Voie (coord. structure)" AS nom_voie,
            "Code postal (coord. structure)" AS code_postal,
            "Libellé commune (coord. structure)" AS commune,
            "Téléphone (coord. structure)" AS telephone,
            "Adresse e-mail (coord. structure)" AS email
        FROM professionnels
        WHERE "Numéro FINESS site" = ?
        LIMIT 1
    """
    structure = pd.read_sql_query(query_structure, conn, params=(finess,)).to_dict(orient="records")
    if not structure:
        conn.close()
        return {"error": "Pharmacie non trouvée"}

    query_pros = """
        SELECT 
            "Libellé profession" AS profession,
            "Nom d'exercice" AS nom,
            "Prénom d'exercice" AS prenom,
            "Libellé civilité" AS civilite,
            "Libellé rôle" AS role
        FROM professionnels
        WHERE "Numéro FINESS site" = ?
    """
    pros = pd.read_sql_query(query_pros, conn, params=(finess,)).to_dict(orient="records")
    conn.close()

    s = structure[0]
    adresse_complete = f"{s['numero_voie'] or ''} {s['type_voie'] or ''} {s['nom_voie'] or ''}".strip()

    return {
        "pharmacie": {
            "finess": s["finess"],
            "nom": s["nom_pharmacie"],
            "enseigne": s["enseigne"],
            "adresse": adresse_complete,
            "code_postal": s["code_postal"],
            "commune": s["commune"],
            "telephone": s["telephone"],
            "email": s["email"]
        },
        "professionnels": pros
    }
