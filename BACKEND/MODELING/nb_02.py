#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import joblib


def train_svm_regression_model(df):
    """
    Entrena modelo SVM con los datos recibidos
    """
    
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT", "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    
    target = "SCORE"
    
    # Crear DataFrame limpio
    model_df = df[features + [target]].copy()
    model_df = model_df.replace([np.inf, -np.inf], np.nan)
    model_df = model_df.dropna()
    
    X = model_df[features]
    y = model_df[target].values.ravel()
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # SVM Pipeline
    svm_model = Pipeline([
        ("scaler", StandardScaler()),
        ("svr", SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.1))
    ])
    
    # Entrenar
    svm_model.fit(X_train, y_train)
    
    # Predicciones
    y_pred = svm_model.predict(X_test)
    
    # Métricas
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print("========== SVM RESULTS ==========")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R2   : {r2:.4f}")
    
    # Guardar modelo
    joblib.dump(svm_model, "svm_score_model.pkl")
    print("Model saved as svm_score_model.pkl")
    
    # Devolver modelo y métricas
    return {
        "model": svm_model,
        "features": features,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "X_test": X_test,
        "y_test": y_test
    }


def train_xgboost_regression_model(df):
    """
    Entrena modelo XGBoost con los datos recibidos
    """
    
    features = [
        "POINTS", "LAPS", "MILLISECONDS", "WEATHER_cloudy",
        "OVERTAKEN_POSITIONS_TOTAL", "DNF_COUNT", "LAPMEAN",
        "PS_COUNT", "SC_COUNT", "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    
    target = "SCORE"
    
    # Crear DataFrame limpio
    model_df = df[features + [target]].copy()
    
    for col in model_df.columns:
        model_df[col] = pd.to_numeric(model_df[col], errors="coerce")
    
    model_df = model_df.replace([np.inf, -np.inf], np.nan)
    model_df = model_df.dropna()
    
    X = model_df[features]
    y = model_df[target]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # XGBoost Model
    xgb_model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )
    
    # Entrenar
    xgb_model.fit(X_train, y_train)
    
    # Predicciones
    y_pred = xgb_model.predict(X_test)
    
    # Métricas
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print("========== XGBOOST RESULTS ==========")
    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R2   : {r2:.4f}")
    
    # Feature importance
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": xgb_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    print("\nTop Feature Importances:")
    print(importance_df)
    
    # Guardar modelo
    joblib.dump(xgb_model, "xgboost_score_model.pkl")
    print("Model saved as xgboost_score_model.pkl")
    
    # Devolver modelo y métricas
    return {
        "model": xgb_model,
        "features": features,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "feature_importance": importance_df,
        "X_test": X_test,
        "y_test": y_test
    }


if __name__ == "__main__":
    # Esto solo se ejecuta si corres el archivo directamente
    # Para pruebas
    df = pd.read_csv("processed_dataset.csv")
    print("Probando SVM...")
    train_svm_regression_model(df)
    print("\nProbando XGBoost...")
    train_xgboost_regression_model(df)
    