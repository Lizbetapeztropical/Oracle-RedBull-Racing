# ==================================================
# INYECCIÓN processed_dataset.csv → MongoDB LOCAL (Docker)
# ==================================================

import pandas as pd
from pymongo import MongoClient
from pathlib import Path
import sys

# ================= CONFIGURATION =================
CSV_PATH = Path(__file__).resolve().parent / "processed_dataset.csv"

MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "processed_races"
# ==================================================

print("🚀 Iniciando proceso de inyección...")

try:
    # 1. Leer CSV
    print(f"📂 Leyendo archivo: {CSV_PATH.name}")
    df = pd.read_csv(CSV_PATH)

    print(f"✅ CSV cargado correctamente:")
    print(f"   → Filas: {len(df)}")
    print(f"   → Columnas: {len(df.columns)}")

    # 2. Convertir NaN a None para MongoDB
    df = df.where(pd.notnull(df), None)

    # 3. Convertir DataFrame a documentos MongoDB
    records = df.to_dict(orient='records')

    print(f"📋 Preparados {len(records)} registros para insertar.")

    # 4. Conexión a MongoDB
    print("🔌 Conectando a MongoDB Local (Docker)...")

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # 5. (Opcional) Limpiar colección antes de insertar
    print("🗑️ Limpiando colección anterior...")
    collection.delete_many({})

    # 6. Insertar documentos
    print("📤 Insertando datos en MongoDB...")

    result = collection.insert_many(
        records,
        ordered=False
    )

    # 7. Resultado final
    print("🎉 ¡Inyección completada con éxito!")

    print(f"   → Documentos insertados: {len(result.inserted_ids)}")
    print(f"   → Base de datos: {DATABASE_NAME}")
    print(f"   → Colección: {COLLECTION_NAME}")

except FileNotFoundError:
    print("❌ Error: No se encontró el archivo processed_dataset.csv")
    print(f"Ruta buscada: {CSV_PATH}")

except Exception as e:
    print("❌ Error durante la inyección:")
    print(e)
    sys.exit(1)

finally:
    try:
        client.close()
    except:
        pass

print("🏁 Fin del script.")
