import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# ==============================================================================
# 1. FUNCIÓN PARA BUSCAR Y CARGAR EL ARCHIVO CSV
# ==============================================================================
def load_data():
    """
    Busca automáticamente la carpeta 'backend' hacia arriba o desde el HOME del usuario
    para localizar recursivamente el archivo 'merged_dataset.csv'.
    """
    start_dir = Path.cwd()
    base_backend = None

    for parent in [start_dir] + list(start_dir.parents):
        if parent.name.lower() == "backend":
            base_backend = parent
            break
        elif (parent / "backend").exists():
            base_backend = parent / "backend"
            break

    if not base_backend:
        home_dir = Path.home()
        backend_dirs = list(home_dir.rglob("backend"))
        if backend_dirs:
            base_backend = backend_dirs[0]

    if not base_backend:
        raise FileNotFoundError("❌ Error: No se pudo localizar ninguna carpeta llamada 'backend' en el sistema.")

    csv_files = list(base_backend.rglob("merged_dataset.csv"))
    if not csv_files:
        raise FileNotFoundError(f"❌ La carpeta 'backend' fue hallada en {base_backend}, pero no contiene 'merged_dataset.csv'.")
        
    csv_path = csv_files[0]
    print(f"🔍 Dataset encontrado de forma dinámica en: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"✅ Datos cargados correctamente: {len(df)} registros.")
    return df

# ==============================================================================
# 2. PROCESAMIENTO, ENTRENAMIENTO Y GUARDADO (REEMPLAZO AUTOMÁTICO EN CARPETA SVM)
# ==============================================================================
def train_xgboost_regression_model(df):
    """
    Entrena el modelo XGBoost usando únicamente métricas numéricas,
    guarda y reemplaza automáticamente los archivos físicos dentro de la carpeta SVM.
    """
    print("\n🔄 Iniciando entrenamiento del modelo XGBoost...")
    df_local = df.copy()

    # FEATURES NUMÉRICAS PURAS (Sin variables encoded)
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT"
    ]
    target = "SCORE"

    # Validar que no falte ninguna columna en tu archivo
    missing_cols = [col for col in (features + [target]) if col not in df_local.columns]
    if missing_cols:
        raise KeyError(f"❌ Error interno: Faltan estas columnas en el archivo: {missing_cols}")

    # Limpieza estricta de datos convirtiendo todo a numérico
    model_df = df_local[features + [target]].copy()
    for col in model_df.columns:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()

    X = model_df[features]
    y = model_df[target].values.ravel()

    # División de conjuntos (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Configuración del hiperparámetro XGBoost
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

    print("🏋️‍♂️ Ajustando árboles de decisión (XGBoost)...")
    xgb_model.fit(X_train, y_train)

    # Predicciones y cálculo de métricas de calidad
    y_pred = xgb_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # Cálculo e impacto de pesos (Feature Importance)
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": xgb_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)

    # Resultados estructurados para el guardado
    xgb_results_df = pd.DataFrame({
        "Actual_SCORE": y_test,
        "Predicted_SCORE": y_pred
    })

    # Forzar que se guarden dentro de tu carpeta SVM/ para que todo quede inyectado ahí
    # Nota: Si ejecutas parado en BACKEND/MODELING, creará/usará la subcarpeta "SVM"
    os.makedirs("SVM", exist_ok=True)
    csv_filename = "SVM/xgboost_results_df.csv"
    pkl_filename = "SVM/xgboost_regression_model.pkl"

    # Escritura y autoreemplazo directo en disco
    xgb_results_df.to_csv(csv_filename, index=False)
    print(f"✅ DataFrame guardado/reemplazado como '{csv_filename}'")
    
    with open(pkl_filename, "wb") as f:
        pickle.dump(xgb_model, f)
    print(f"✅ Modelo guardado/reemplazado como '{pkl_filename}'")

    print("\n" + "="*50)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*50)

    return {
        "model": xgb_model,
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
        # Carga del dataset unificado
        df_origen = load_data()
        
        # Ejecución del pipeline XGBoost
        resultado = train_xgboost_regression_model(df_origen)

        # Formato de salida exclusivo solicitado (OUTPUT)
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
        print(f"\n❌ Ocurrió un error inesperado en XGBoost: {e}")