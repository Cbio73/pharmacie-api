import pandas as pd
import sqlite3

CSV_FILE = "pharmacies_et_dieteticiens_filtrés.csv"
DB_FILE = "pharmacie.db"

df = pd.read_csv(CSV_FILE, sep=",", encoding="utf-8", dtype=str)
conn = sqlite3.connect(DB_FILE)
df.to_sql("professionnels", conn, if_exists="replace", index=False)
conn.close()

print(f"✅ Base '{DB_FILE}' créée avec {len(df)} lignes.")