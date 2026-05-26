# ==============================================================================
# INYECCIÓN processed_dataset → MongoDB LOCAL (Docker)
# =============================================================================

import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import sys

# ================= CONFIGURATION =================
BASE_DIR = Path(__file__).resolve().parent
MERGED_CSV_PATH = BASE_DIR / "merged_dataset.csv"
OUTPUT_CSV_PATH = BASE_DIR / "processed_dataset.csv"

MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "processed_dataset"
# ==================================================

print("🚀 Iniciando proceso de Feature Engineering e Inyección...")

try:
    # 1. Leer Dataset
    print(f"📂 Leyendo merged_dataset.csv...")
    if not MERGED_CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {MERGED_CSV_PATH}")
        
    df = pd.read_csv(MERGED_CSV_PATH)
    print(f"✅ CSV cargado correctamente: {len(df)} registros")

    # 2. Feature Engineering
    print("⚙️ Aplicando Feature Engineering...")
    df = df.sort_values(by=["YEAR", "RACEID"])

    df["ROLLING_POINTS"] = (
        df.groupby("DRIVERID")["POINTS"]
        .transform(lambda x: x.rolling(5, min_periods=1).mean())
    )

    df["ROLLING_LAP"] = (
        df.groupby("DRIVERID")["LAPMEAN"]
        .transform(lambda x: x.rolling(5, min_periods=1).mean())
    )

    df["LAP_CONSISTENCY"] = (
        df.groupby("DRIVERID")["LAPMEAN"]
        .transform(lambda x: x.rolling(5).std())
    )

    df["RACE_INTERRUPTIONS"] = df["SC_COUNT"] + df["PS_COUNT"]

    df["OVERTAKE_RATIO"] = df["OVERTAKEN_POSITIONS_TOTAL"] / df["LAPS"]

    # Encodings
    driver_encoder = LabelEncoder()
    race_encoder = LabelEncoder()

    df["DRIVER_ENCODED"] = driver_encoder.fit_transform(df["DRIVERREF"])
    df["RACE_ENCODED"] = race_encoder.fit_transform(df["NAME_YEAR"])

    # Reemplazar NaN por None para MongoDB
    df = df.replace({np.nan: None})

    # 3. Guardar respaldo local
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"💾 Processed dataset guardado: {OUTPUT_CSV_PATH.name}")

    # 4. Convertir a formato MongoDB
    records = df.to_dict('records')
    print(f"📋 Preparados {len(records)} registros para insertar.")

    # 5. Conectar a MongoDB
    print("🔌 Conectando a MongoDB Local...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # 6. Limpiar colección anterior
    collection.delete_many({})
    print("🗑️ Colección anterior limpiada.")

    # 7. Insertar nuevos datos
    result = collection.insert_many(records, ordered=False)

    print("🎉 ¡Inyección completada con éxito!")
    print(f"   → Insertados {len(result.inserted_ids)} documentos")
    print(f"   → Colección: {COLLECTION_NAME}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error durante el proceso: {e}")
    sys.exit(1)

print("Fin del script.")