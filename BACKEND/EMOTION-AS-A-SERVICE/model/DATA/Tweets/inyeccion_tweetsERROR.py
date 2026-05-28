# ============================================================================
# RESPALDO DE tweets_cleaned.csv A MONGODB
# ============================================================================

from pathlib import Path
import pandas as pd
from pymongo import MongoClient

# ================= CONFIGURACIÓN =================
CSV_PATH = Path(__file__).resolve().parent / "tweets_cleaned.csv"
MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "tweets_cleaned_backup"

# ================= FUNCIÓN PARA GUARDAR =================
def guardar_csv_en_mongodb():
    """Guarda el contenido de tweets_cleaned.csv en MongoDB"""
    
    try:
        # Verificar que el archivo existe
        if not CSV_PATH.exists():
            print(f"❌ No se encuentra: {CSV_PATH}")
            print("   Ejecuta primero la limpieza para generar el archivo")
            return False
        
        # Conectar a MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Leer el CSV
        print(f"📥 Leyendo {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)
        print(f"   ✅ {len(df):,} filas, {len(df.columns)} columnas")
        
        # Convertir DataFrame a diccionario
        datos = df.to_dict(orient='records')
        
        # Crear documento
        documento = {
            "nombre_archivo": "tweets_cleaned.csv",
            "ruta": str(CSV_PATH),
            "total_filas": len(df),
            "total_columnas": len(df.columns),
            "columnas": df.columns.tolist(),
            "datos": datos,
            "fecha_respaldo": pd.Timestamp.now(),
            "version": 1
        }
        
        # Insertar en MongoDB
        result = collection.insert_one(documento)
        
        print(f"\n✅ CSV guardado en MongoDB")
        print(f"   Base de datos: {DATABASE_NAME}")
        print(f"   Colección: {COLLECTION_NAME}")
        print(f"   ID: {result.inserted_id}")
        print(f"   Filas: {len(df):,}")
        print(f"   Columnas: {len(df.columns)}")
        
        # Cerrar conexión
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar en MongoDB: {e}")
        return False

# ================= EJECUTAR =================
if __name__ == "__main__":
    guardar_csv_en_mongodb()