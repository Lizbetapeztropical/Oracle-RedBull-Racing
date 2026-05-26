# ==================================================================================
# INYECCIÓN RESPALDO: Guardar Notebook 03.ipynb → MongoDB LOCAL (Docker)
# ==================================================================================

import json
from pymongo import MongoClient
from pathlib import Path
import sys

# ================= CONFIGURATION =================
# Busca el archivo 03.ipynb en la misma carpeta que este script
NOTEBOOK_PATH = Path(__file__).resolve().parent / "03.ipynb"
PTH_PATH = Path(__file__).resolve().parent / "f1_pytorch_model.pth"

MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "03_notebook"
# ==================================================

print("🚀 Iniciando proceso de inyección del Notebook...")

try:
    # 1. Leer el archivo .ipynb (Los notebooks son archivos JSON por dentro)
    print(f"📂 Leyendo archivo: {NOTEBOOK_PATH.name}")
    
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        notebook_content = json.load(f)

    print(f"✅ Notebook cargado correctamente.")
    print(f"   → Celdas encontradas: {len(notebook_content.get('cells', []))}")

    # 2. Preparar el documento para MongoDB
    # Guardamos el contenido completo del notebook junto con metadata útil
    backup_document = {
        "filename": NOTEBOOK_PATH.name,
        "description": "Pipeline de extracción y procesamiento de datos F1",
        "content": notebook_content
    }

    # 3. Conexión a MongoDB
    print("🔌 Conectando a MongoDB Local (Docker)...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # 4. Limpiar respaldos anteriores del mismo notebook (para no duplicar)
    print(f"🗑️ Limpiando versiones anteriores de {NOTEBOOK_PATH.name}...")
    collection.delete_many({"filename": NOTEBOOK_PATH.name})

    # 5. Insertar el Notebook
    print("📤 Insertando archivo en MongoDB...")
    result = collection.insert_one(backup_document)

    # 6. Resultado final
    print("🎉 ¡Inyección del Notebook completada con éxito!")
    print(f"   → ID del documento: {result.inserted_id}")
    print(f"   → Base de datos: {DATABASE_NAME}")
    print(f"   → Colección: {COLLECTION_NAME}")

except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo literal '02.ipynb'")
    print(f"Ruta buscada: {NOTEBOOK_PATH}")

except json.JSONDecodeError:
    print("❌ Error: El archivo 02.ipynb no tiene un formato JSON válido o está corrupto.")

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