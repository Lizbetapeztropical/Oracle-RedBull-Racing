# ==============================================================================
# INYECCIÓN processed_dataset → MongoDB LOCAL (Docker)
# ==============================================================================

import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import sys

# ================= CONFIGURATION =================
# Path calcula la ruta automática dentro de la carpeta donde esté guardado este script
BASE_DIR = Path(__file__).resolve().parent
MERGED_CSV_PATH = BASE_DIR / "merged_dataset.csv"
TWEETS_CSV_PATH = BASE_DIR / "tweets.csv"
OUTPUT_CSV_PATH = BASE_DIR / "processed_dataset.csv"

# Credenciales unificadas del Docker de tu equipo
MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "processed_dataset"
# ==================================================

print("🚀 Iniciando proceso de Feature Engineering e Inyección...")

try:
    # 1. Leer Datasets
    print(f"📂 Leyendo archivos de origen...")
    if not MERGED_CSV_PATH.exists() or not TWEETS_CSV_PATH.exists():
        raise FileNotFoundError("Falta alguno de los archivos CSV de origen en la carpeta.")
        
    df = pd.read_csv(MERGED_CSV_PATH)
    tweets = pd.read_csv(TWEETS_CSV_PATH)
    
    print(f"✅ CSVs cargados correctamente. Procesando variables de carrera...")

    # 2. Feature Engineering
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

    df["RACE_INTERRUPTIONS"] = (
        df["SC_COUNT"] + df["PS_COUNT"]
    )

    df["OVERTAKE_RATIO"] = (
        df["OVERTAKEN_POSITIONS_TOTAL"] / df["LAPS"]
    )

    # Encodings
    driver_encoder = LabelEncoder()
    race_encoder = LabelEncoder()

    df["DRIVER_ENCODED"] = driver_encoder.fit_transform(df["DRIVERREF"])
    df["RACE_ENCODED"] = race_encoder.fit_transform(df["NAME_YEAR"])

    # Reemplazar NaN por None para que MongoDB no falle al insertar
    df = df.replace({np.nan: None})

    # 3. Guardar respaldo local en CSV
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"💾 Respaldo local guardado en: {OUTPUT_CSV_PATH.name}")

    # 4. Convertir a formato MongoDB (Diccionario)
    records = df.to_dict('records')
    print(f"📋 Preparados {len(records)} registros procesados para insertar.")

    # 5. Conectar a MongoDB
    print("🔌 Conectando a MongoDB Local (Docker)...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # 6. Limpiar datos viejos para evitar duplicados
    print(f"🗑️ Limpiando la colección '{COLLECTION_NAME}'...")
    collection.delete_many({})

    # 7. Insertar datos nuevos
    print("📤 Insertando datos en la colección...")
    result = collection.insert_many(records, ordered=False)

    print("🎉 ¡Inyección completada con éxito!")
    print(f"   → Se insertaron {len(result.inserted_ids)} documentos.")
    print(f"   → Base de datos: {DATABASE_NAME}")
    print(f"   → Colección: {COLLECTION_NAME}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error durante el proceso:")
    print(e)
    sys.exit(1)

print("Fin del script.")