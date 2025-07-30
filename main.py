import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacie.db")
conn = sqlite3.connect(DB_PATH)

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
def get_pharmacies(departement: str, ville: str = None):
    conn = sqlite3.connect("pharmacie.db")
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
