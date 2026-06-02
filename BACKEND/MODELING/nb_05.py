#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
from pathlib import Path


def train_linear_regression_model():
    """
    Entrena modelo de regresión lineal con processed_dataset.csv
    """
    # ============================================
    # CARGAR DATOS (ruta desde BACKEND/MODELING)
    # ============================================
    
    BASE_DIR = Path(__file__).resolve().parent
    CSV_PATH = BASE_DIR / "processed_dataset.csv"
    
    print("📂 Cargando archivo processed_dataset.csv...")
    print(f"📁 Ruta: {CSV_PATH.resolve()}")
    
    if not CSV_PATH.exists():
        print(f"❌ Error: No se encuentra {CSV_PATH}")
        print("Ejecuta primero 01.ipynb para generar processed_dataset.csv")
        return None
    
    df = pd.read_csv(CSV_PATH)
    
    print(f"✅ Datos cargados correctamente:")
    print(f"   → Filas: {len(df)}")
    print(f"   → Columnas: {len(df.columns)}")
    
    # ============================================
    # FEATURES & TARGET
    # ============================================
    
    features = [
        "POINTS",
        "LAPS",
        "MILLISECONDS",
        "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL",
        "DNF_COUNT",
        "LAPMEAN",
        "PS_COUNT",
        "SC_COUNT"
    ]
    
    target = "SCORE"
    
    # Verificar columnas
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        print(f"❌ Columnas faltantes: {missing_features}")
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        return None
    
    print("✅ Todas las columnas necesarias están presentes")
    
    # ============================================
    # CLEAN DATA
    # ============================================
    
    model_df = df[features + [target]].copy()
    model_df = model_df.replace([np.inf, -np.inf], np.nan)
    original_len = len(model_df)
    model_df = model_df.dropna()
    
    print(f"🧹 Limpieza de datos:")
    print(f"   → Filas originales: {original_len}")
    print(f"   → Filas después de limpieza: {len(model_df)}")
    
    # ============================================
    # X & y
    # ============================================
    
    X = model_df[features]
    y = model_df[target].values.ravel()
    
    # ============================================
    # TRAIN TEST SPLIT
    # ============================================
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"📊 División de datos:")
    print(f"   → Train: {len(X_train)} filas")
    print(f"   → Test: {len(X_test)} filas")
    
    # ============================================
    # PIPELINE & TRAIN
    # ============================================
    
    linear_model = Pipeline([
        ("scaler", StandardScaler()),
        ("linear_regression", LinearRegression())
    ])
    
    print("🏋️ Entrenando modelo...")
    linear_model.fit(X_train, y_train)
    
    # ============================================
    # PREDICTIONS
    # ============================================
    
    y_pred = linear_model.predict(X_test)
    
    # ============================================
    # METRICS
    # ============================================
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"📈 Métricas del modelo:")
    print(f"   → MAE: {mae:.4f}")
    print(f"   → RMSE: {rmse:.4f}")
    print(f"   → R²: {r2:.4f}")
    
    # ============================================
    # PREDICTIONS DF (nombre personalizado)
    # ============================================
    
    lm_saved_csv = pd.DataFrame({
        "Actual_SCORE": y_test,
        "Predicted_SCORE": y_pred,
        "Error": abs(y_test - y_pred)
    })
    
    # ============================================
    # FEATURE IMPORTANCE
    # ============================================
    
    coefficients = linear_model.named_steps["linear_regression"].coef_
    
    feature_importance = pd.DataFrame({
        "Feature": features,
        "Coefficient": coefficients
    }).sort_values(by="Coefficient", ascending=False)
    
    print("\n🏆 Top 5 características más importantes:")
    print(feature_importance.head(5).to_string(index=False))
    
    # ============================================
    # GUARDAR ARCHIVOS
    # ============================================
    
    csv_filename = "lm_score_predictions.csv"
    lm_saved_csv.to_csv(csv_filename, index=False)
    print(f"\n✅ DataFrame guardado como '{csv_filename}'")
    
    pkl_filename = "linear_regression_model.pkl"
    with open(pkl_filename, 'wb') as f:
        pickle.dump(linear_model, f)
    print(f"✅ Modelo guardado como '{pkl_filename}'")
    
    print("\n" + "="*50)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*50)
    
    return {
        "model": linear_model,
        "predictions_df": lm_saved_csv,
        "saved_csv": csv_filename,
        "saved_pickle": pkl_filename,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "feature_importance": feature_importance
    }


# ============================================
# EJECUTAR LA FUNCIÓN
# ============================================

if __name__ == "__main__":
    resultado = train_linear_regression_model()
    
    if resultado:
        print("\n📊 RESULTADOS DEL MODELO:")
        print(f"   → R²: {resultado['r2']:.4f}")
        print(f"   → MAE: {resultado['mae']:.4f}")
        print(f"   → DataFrame: {resultado['saved_csv']}")
        print(f"   → Modelo PKL: {resultado['saved_pickle']}")
        