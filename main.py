from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacie.db")

@app.get("/pharmacies")
def get_pharmacies(departement: str, ville: str = None):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        print(f"📦 Connexion locale à {DB_PATH}")

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
        conn.close()
        print(f"✅ {len(df)} lignes retournées")
        return df.to_dict(orient="records")

    except Exception as e:
        print(f"❌ Erreur dans /pharmacies : {e}")
        return {"error": str(e)}
