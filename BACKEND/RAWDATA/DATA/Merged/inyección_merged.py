# ==================================================
# INYECCIÓN merged_dataset.csv → MongoDB LOCAL (Docker)
# ==================================================

import pandas as pd
from pymongo import MongoClient
from pathlib import Path
import sys

# ================= CONFIGURATION =================
CSV_PATH = Path(__file__).resolve().parent / "merged_dataset.csv"

MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "merged_races"
# ==================================================

print("🚀 Iniciando proceso de inyección...")

try:
    # 1. Leer CSV
    print(f"📂 Leyendo archivo: {CSV_PATH.name}")
    df = pd.read_csv(CSV_PATH)
    print(f"✅ CSV cargado correctamente: {len(df)} filas y {len(df.columns)} columnas.")

    # 2. Convertir a formato MongoDB
    records = df.to_dict('records')
    print(f"📋 Preparados {len(records)} registros para insertar.")

    # 3. Conectar a MongoDB
    print("🔌 Conectando a MongoDB Local (Docker)...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # 4. Insertar datos
    print("📤 Insertando datos en la colección...")
    result = collection.insert_many(records, ordered=False)

    print("🎉 ¡Inyección completada con éxito!")
    print(f"   → Se insertaron {len(result.inserted_ids)} documentos.")
    print(f"   → Base de datos: {DATABASE_NAME}")
    print(f"   → Colección: {COLLECTION_NAME}")

except FileNotFoundError:
    print("❌ Error: No se encontró el archivo merged_dataset.csv")
    print(f"Ruta buscada: {CSV_PATH}")
except Exception as e:
    print(f"❌ Error durante la inyección:")
    print(e)
    sys.exit(1)

print("Fin del script.")
