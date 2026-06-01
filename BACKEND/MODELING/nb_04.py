#!/usr/bin/env python
# coding: utf-8

# In[3]:


# ==================================================
# MLP SCORE MODEL
# ==================================================

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ==================================================
# TRAIN MLP MODEL
# ==================================================

def train_mlp_score_model(df):
    """
    Entrena un modelo MLP para predecir SCORE
    """
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

    # ============================================
    # CLEAN DATA
    # ============================================

    model_df = df[features + [target]].copy()

    model_df = model_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    model_df = model_df.dropna()

    # ============================================
    # X & y
    # ============================================

    X = model_df[features]

    y = model_df[target].values.ravel()

    # ============================================
    # TRAIN TEST SPLIT
    # ============================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # ============================================
    # MLP PIPELINE
    # ============================================

    mlp_model = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "mlp",
            MLPRegressor(
                hidden_layer_sizes=(128, 64, 32),
                activation="relu",
                solver="adam",
                alpha=0.0001,
                learning_rate="adaptive",
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        )
    ])

    # ============================================
    # TRAIN
    # ============================================

    mlp_model.fit(
        X_train,
        y_train
    )

    # ============================================
    # PREDICT
    # ============================================

    y_pred = mlp_model.predict(
        X_test
    )

    # ============================================
    # METRICS
    # ============================================

    mae = mean_absolute_error(
        y_test,
        y_pred
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            y_pred
        )
    )

    r2 = r2_score(
        y_test,
        y_pred
    )

    # ============================================
    # OUTPUT DATAFRAME (nombre personalizado)
    # ============================================

    mlp_score_predictions_df = pd.DataFrame({
        "Actual_SCORE": y_test,
        "Predicted_SCORE": y_pred,
        "Absolute_Error": np.abs(y_test - y_pred)
    })

    # ============================================
    # SAVE CSV (REPLACE IF EXISTS)
    # ============================================

    csv_path = "mlp_score_predictions.csv"

    mlp_score_predictions_df.to_csv(
        csv_path,
        index=False
    )
    print(f"✅ DataFrame guardado como '{csv_path}'")

    # ============================================
    # SAVE PICKLE (REPLACE IF EXISTS)
    # ============================================

    pickle_path = "mlp_score_model.pkl"

    joblib.dump(
        mlp_model,
        pickle_path
    )
    print(f"✅ Modelo guardado como '{pickle_path}'")

    # ============================================
    # RETURN (incluye DataFrame y pickle generados)
    # ============================================

    return {
        "model": mlp_model,
        "predictions_df": mlp_score_predictions_df,
        "saved_csv": csv_path,
        "saved_pickle": pickle_path,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }


# ==================================================
# EXECUTION (al final del archivo)
# ==================================================

if __name__ == "__main__":
    # Cargar datos desde la ruta correcta
    CSV_PATH = Path("../../BACKEND/RAWDATA/DATA/Merged/merged_dataset.csv")
    
    print("📂 Cargando archivo merged_dataset.csv...")
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")

    resultado_mlp_score = train_mlp_score_model(df)

    print("\n" + "="*50)
    print("📊 RESULTADOS MLP SCORE MODEL")
    print("="*50)
    print(f"MAE  : {resultado_mlp_score['mae']:.4f}")
    print(f"RMSE : {resultado_mlp_score['rmse']:.4f}")
    print(f"R²   : {resultado_mlp_score['r2']:.4f}")

    print("\n📁 Archivos generados:")
    print(f"   → CSV: {resultado_mlp_score['saved_csv']}")
    print(f"   → PKL: {resultado_mlp_score['saved_pickle']}")

    print("\n🔍 Primeras predicciones:")
    print(resultado_mlp_score["predictions_df"].head())
    
    

