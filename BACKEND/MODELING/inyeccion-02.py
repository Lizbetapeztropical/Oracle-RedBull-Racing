# ==============================================================================
# INYECCIÓN METRICAS MODELOS (SVM & XGBOOST) → MongoDB LOCAL (Docker)
# ==============================================================================

import pandas as pd
import numpy as np
from pymongo import MongoClient
from pathlib import Path
import sys
import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import joblib

# ================= CONFIGURATION =================
BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV_PATH = BASE_DIR / "processed_dataset.csv"

# Modelos de guardado local (Respaldos)
SVM_MODEL_PATH = BASE_DIR / "svm_score_model.pkl"
XGB_MODEL_PATH = BASE_DIR / "xgboost_score_model.pkl"

# Credenciales unificadas del Docker de tu equipo
MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "resultados_modelos"
# ==================================================

print("🚀 Iniciando entrenamiento de modelos e Inyección de Métricas...")

try:
    # 1. Leer dataset procesado
    print(f"📂 Leyendo archivo de origen: {INPUT_CSV_PATH.name}")
    if not INPUT_CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {INPUT_CSV_PATH.name}. Ejecuta primero el script 01.")
        
    df = pd.read_csv(INPUT_CSV_PATH)
    
    # 2. Configurar Variables
    features = [
        "DRIVER_POINTS_BEFORE_RACE", "LAPS", "MILLISECONDS", "WEATHER_rain",
        "WEATHER_WET", "WEATHER_cloudy", "OVERTAKEN_POSITIONS_TOTAL",
        "DNF_COUNT", "LAPMEAN", "FASTESTLAP", "PS_COUNT", "SC_COUNT",
        "ROLLING_POINTS", "ROLLING_LAP", "LAP_CONSISTENCY", "RACE_INTERRUPTIONS",
        "OVERTAKE_RATIO", "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    target = "SCORE"

    # Limpieza común de infinitos y nulos para entrenamiento
    model_df = df[features + [target]].copy()
    for col in model_df.columns:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()

    X = model_df[features]
    y = model_df[target].values.ravel()

    # Dividir entrenamiento / prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ==========================================================================
    # ENTRENAMIENTO Y EVALUACIÓN: SVM
    # ==========================================================================
    print("🤖 Entrenando SVM (SVR)...")
    svm_model = Pipeline([
        ("scaler", StandardScaler()),
        ("svr", SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.1))
    ])
    svm_model.fit(X_train, y_train)
    y_pred_svm = svm_model.predict(X_test)
    joblib.dump(svm_model, SVM_MODEL_PATH)

    svm_metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred_svm)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_svm))),
        "r2": float(r2_score(y_test, y_pred_svm))
    }

    # ==========================================================================
    # ENTRENAMIENTO Y EVALUACIÓN: XGBOOST
    # ==========================================================================
    print("⚡ Entrenando XGBoost...")
    xgb_model = XGBRegressor(
        n_estimators=500, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8, objective="reg:squarederror", random_state=42
    )
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)
    joblib.dump(xgb_model, XGB_MODEL_PATH)

    xgb_metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred_xgb)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_xgb))),
        "r2": float(r2_score(y_test, y_pred_xgb))
    }

    # Extraer Feature Importances de XGBoost ordenados
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": xgb_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    xgb_feature_importance = importance_df.to_dict(orient="records")

    # ==========================================================================
    # PREPARACIÓN DEL DOCUMENTO PARA MONGODB
    # ==========================================================================
    # Creamos un único documento con la marca de tiempo de la ejecución
    documento_resultados = {
        "fecha_ejecucion": datetime.datetime.now(datetime.timezone.utc),
        "modelos": {
            "svm": {
                "nombre": "Support Vector Regression",
                "metricas": svm_metrics,
                "dataset_origen": INPUT_CSV_PATH.name
            },
            "xgboost": {
                "nombre": "XGBoost Regressor",
                "metricas": xgb_metrics,
                "feature_importance": xgb_feature_importance,
                "dataset_origen": INPUT_CSV_PATH.name
            }
        }
    }

    # ==========================================================================
    # CONEXIÓN E INYECCIÓN A MONGODB
    # ==========================================================================
    print("🔌 Conectando a MongoDB Local (Docker)...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Insertamos las métricas calculadas en la colección
    print(f"📤 Inyectando métricas en la colección '{COLLECTION_NAME}'...")
    result = collection.insert_one(documento_resultados)

    print("🎉 ¡Inyección de métricas completada con éxito!")
    print(f"   → ID del documento: {result.inserted_id}")
    print(f"   → Base de datos: {DATABASE_NAME}")
    print(f"   → Colección: {COLLECTION_NAME}")
    print(f"   📊 [SVM]     R2: {svm_metrics['r2']:.4f} | MAE: {svm_metrics['mae']:.4f}")
    print(f"   📊 [XGBOOST] R2: {xgb_metrics['r2']:.4f} | MAE: {xgb_metrics['mae']:.4f}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error durante el proceso:")
    print(e)
    sys.exit(1)

print("Fin del script.")