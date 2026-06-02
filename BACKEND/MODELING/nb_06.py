import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

# ==============================================================================
# 1. FUNCIÓN PARA CARGAR processed_dataset.csv
# ==============================================================================
def load_data():
    """
    Carga el archivo processed_dataset.csv desde la carpeta BACKEND/MODELING
    """
    # Obtener la ruta base del script (BACKEND/MODELING)
    script_dir = Path(__file__).resolve().parent
    csv_path = script_dir / "processed_dataset.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"❌ Error: No se encuentra {csv_path}")
    
    print(f"🔍 Dataset encontrado en: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✅ Datos cargados correctamente: {len(df)} registros.")
    return df

# ==============================================================================
# 2. PROCESAMIENTO, ENTRENAMIENTO Y GUARDADO (CON AUTO-ENCODING EN MEMORIA)
# ==============================================================================
def train_xgboost_regression_model(df):
    """
    Detecta columnas de piloto/carrera, genera el encoding en caliente en memoria,
    y entrena el modelo XGBoost guardando los resultados en la carpeta del script.
    """
    print("\n🔄 Iniciando ingeniería de variables y entrenamiento XGBoost...")
    df_local = df.copy()

    # --- IDENTIFICACIÓN AUTOMÁTICA DE COLUMNAS DE CONTEXTO ---
    col_piloto = None
    for col in ["DRIVER_ENCODED", "driverRef", "driverId", "DRIVERID", "DRIVERREF"]:
        if col in df_local.columns:
            col_piloto = col
            break
            
    col_carrera = None
    for col in ["RACE_ENCODED", "raceId", "name_year", "RACEID", "CIRCUITID"]:
        if col in df_local.columns:
            col_carrera = col
            break

    if not col_piloto or not col_carrera:
        raise KeyError(f"❌ Error: No se encontraron columnas de piloto o carrera en tu CSV. Columnas disponibles: {list(df_local.columns)[:15]}")

    print(f"📦 Mapeando pilotos desde: '{col_piloto}' y carreras desde: '{col_carrera}'")

    # Crear la codificación numérica en caliente
    le_driver = LabelEncoder()
    le_race = LabelEncoder()
    
    df_local["DRIVER_ENCODED"] = le_driver.fit_transform(df_local[col_piloto].astype(str))
    df_local["RACE_ENCODED"] = le_race.fit_transform(df_local[col_carrera].astype(str))

    # --- FEATURES FINALES ---
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT", 
        "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    target = "SCORE"

    # Verificar resto de métricas numéricas
    missing_num_cols = [col for col in features[:-2] if col not in df_local.columns]
    if missing_num_cols:
        raise KeyError(f"❌ Error interno: Faltan estas columnas numéricas básicas en tu CSV: {missing_num_cols}")

    # Filtrado y limpieza estricta
    model_df = df_local[features + [target]].copy()
    
    for col in model_df.columns:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()

    X = model_df[features]
    y = model_df[target].values.ravel()

    # Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Hiperparámetros de XGBoost
    xgb_model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        eval_metric="rmse"
    )

    print("🏋️‍♂️ Ajustando árboles de decisión con contexto histórico (XGBoost)...")
    xgb_model.fit(X_train, y_train)

    # Métricas
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # Importancia de variables
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": xgb_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    xgb_results_df = pd.DataFrame({
        "Actual_SCORE": y_test,
        "Predicted_SCORE": y_pred
    })

    # ENRUTAMIENTO DINÁMICO (Se guarda donde se ubica este archivo .py)
    script_dir = Path(__file__).parent.resolve()
    
    # Guardar archivos
    csv_filename = str(script_dir / "xgboost_results_df.csv")
    pkl_filename = str(script_dir / "xgboost_regression_model.pkl")

    xgb_results_df.to_csv(csv_filename, index=False)
    print(f"✅ DataFrame guardado en: '{csv_filename}'")
    
    with open(pkl_filename, "wb") as f:
        pickle.dump(xgb_model, f)
    print(f"✅ Modelo guardado en: '{pkl_filename}'")

    print("\n" + "="*50)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*50)

    return {
        "saved_csv": csv_filename,
        "saved_pickle": pkl_filename,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "feature_importance": importance_df
    }

# ==============================================================================
# 3. BLOQUE DE EJECUCIÓN ESTÁNDAR Y REPORTES (OUTPUT)
# ==============================================================================
if __name__ == "__main__":
    try:
        # 1. Cargar el dataset
        df_origen = load_data()
        
        # 2. Correr el entrenamiento
        resultado = train_xgboost_regression_model(df_origen)

        if resultado:
            print("\n📊 RESULTADOS DEL MODELO XGBOOST:")
            print(f"   → R²: {resultado['r2']:.4f}")
            print(f"   → MAE: {resultado['mae']:.4f}")
            print(f"   → RMSE: {resultado['rmse']:.4f}")
            print(f"   → DataFrame: {resultado['saved_csv']}")
            print(f"   → Modelo PKL: {resultado['saved_pickle']}")
            
            print("\n🔝 TOP FEATURES MÁS IMPORTANTES:")
            for idx, row in resultado['feature_importance'].head(3).iterrows():
                print(f"   ⭐ {row['Feature']}: {row['Importance']:.4f}")
            print()
            
    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")
        