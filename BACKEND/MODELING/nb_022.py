import os
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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
# 2. PROCESAMIENTO, ENTRENAMIENTO Y GUARDADO
# ==============================================================================
def train_svm_regression_model(df):
    """
    Entrena el modelo SVM usando únicamente las métricas numéricas puras de carrera
    y sobrescribe automáticamente los archivos resultantes en disco.
    """
    df_local = df.copy()

    # VARIABLES ÚNICAMENTE NUMÉRICAS (Sin DRIVERREF ni NAME_YEAR)
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

    # Limpieza estricta de nulos e infinitos
    model_df = df_local[features + [target]].copy()
    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()

    X = model_df[features]
    y = model_df[target].values.ravel()

    # División de conjuntos (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Pipeline simplificado (Solo escalado estándar + SVM)
    svm_model = Pipeline([
        ("scaler", StandardScaler()),
        ("svr", SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.1))
    ])

    # Entrenamiento del modelo
    print("🏋️‍♂️ Entrenando el modelo SVM con variables numéricas...")
    svm_model.fit(X_train, y_train)

    # Generación de Predicciones y cálculo de métricas
    y_pred = svm_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # Dataset de resultados estructurado para el reporte
    svm_results_df = pd.DataFrame({
        "Actual_SCORE": y_test,
        "Predicted_SCORE": y_pred
    })

    # Nombres de los archivos físicos de salida (Se sobrescriben automáticamente)
    csv_filename = "svm_score_predictions.csv"
    pkl_filename = "svm_regression_model.pkl"

    # Escritura física sin duplicar nombres
    svm_results_df.to_csv(csv_filename, index=False)
    print(f"\n✅ DataFrame guardado/reemplazado como '{csv_filename}'")
    
    with open(pkl_filename, 'wb') as f:
        pickle.dump(svm_model, f)
    print(f"✅ Modelo guardado/reemplazado como '{pkl_filename}'")
    
    print("\n" + "="*50)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*50)
    
    return {
        "model": svm_model,
        "predictions_df": svm_results_df,
        "saved_csv": csv_filename,
        "saved_pickle": pkl_filename,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }

# ==============================================================================
# 3. BLOQUE DE EJECUCIÓN ESTÁNDAR (.PY)
# ==============================================================================
if __name__ == "__main__":
    try:
        # Carga desde processed_dataset.csv
        df_origen = load_data()
        
        # Ejecución del pipeline y guardado de artefactos
        resultado = train_svm_regression_model(df_origen)

        # Bloque único de salida por consola
        if resultado:
            print("\n📊 RESULTADOS DEL MODELO SVM:")
            print(f"   → R²: {resultado['r2']:.4f}")
            print(f"   → MAE: {resultado['mae']:.4f}")
            print(f"   → RMSE: {resultado['rmse']:.4f}")
            print(f"   → DataFrame: {resultado['saved_csv']}")
            print(f"   → Modelo PKL: {resultado['saved_pickle']}")
            
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")
        