# ==============================================================================
# INYECCIÓN PYTORCH & ENSEMBLES → MongoDB LOCAL (Docker)
# ==============================================================================

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor

from pymongo import MongoClient
from pathlib import Path
import sys
import datetime

# ================= CONFIGURATION =================
BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV_PATH = BASE_DIR / "processed_dataset.csv"

# Rutas para guardar los pesos de la red y los modelos locales
PYTORCH_MODEL_PATH = BASE_DIR / "f1_pytorch_model.pth"

# Credenciales unificadas del Docker de tu equipo
MONGO_URI = "mongodb://admin:oracle@localhost:27017/"
DATABASE_NAME = "redbull_racing"
COLLECTION_NAME = "resultados_modelos"  # Misma colección para centralizar analíticas
# ==================================================

# Definición de la arquitectura de la red (Debe declararse para inicializar el modelo)
class F1NeuralNetwork(nn.Module):
    def __init__(self, input_size):
        super(F1NeuralNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.30),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    def forward(self, x):
        return self.network(x)

print("🚀 Iniciando entrenamiento avanzado e Inyección a MongoDB...")

try:
    # 1. Leer dataset procesado
    if not INPUT_CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo {INPUT_CSV_PATH.name}. Corre primero el script 01.")
    df = pd.read_csv(INPUT_CSV_PATH)
    
    # Variables de entrada y salida
    features = [
        "DRIVER_POINTS_BEFORE_RACE", "LAPS", "MILLISECONDS", "WEATHER_rain",
        "WEATHER_WET", "WEATHER_cloudy", "OVERTAKEN_POSITIONS_TOTAL",
        "DNF_COUNT", "LAPMEAN", "FASTESTLAP", "PS_COUNT", "SC_COUNT",
        "ROLLING_POINTS", "ROLLING_LAP", "LAP_CONSISTENCY", "RACE_INTERRUPTIONS",
        "OVERTAKE_RATIO", "DRIVER_ENCODED", "RACE_ENCODED"
    ]
    target = "SCORE"

    # Limpieza de datos
    model_df = df[features + [target]].copy()
    model_df = model_df.replace([np.inf, -np.inf], np.nan).dropna()

    X = model_df[features]
    y = model_df[target].values

    # Split y Escalado
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ==========================================================================
    # 2. ENTRENAMIENTO PYTORCH
    # ==========================================================================
    print("🧠 Entrenando Red Neuronal en PyTorch...")
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1,1)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1,1)

    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    model = F1NeuralNetwork(X_train.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

    epochs = 200
    for epoch in range(epochs):
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)
            loss.backward()
            optimizer.step()

    # Evaluación PyTorch
    model.eval()
    with torch.no_grad():
        y_pred_tensor = model(X_test_tensor)
    y_pred_nn = y_pred_tensor.numpy().flatten()

    # Métricas Red Neuronal
    nn_metrics = {
        "mae": float(mean_absolute_error(y_test, y_pred_nn)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred_nn))),
        "r2": float(r2_score(y_test, y_pred_nn))
    }

    # Guardar pesos locales
    torch.save(model.state_dict(), PYTORCH_MODEL_PATH)

    # ==========================================================================
    # 3. MODELOS ENSEMBLE (ÁRBOLES)
    # ==========================================================================
    print("🌲 Entrenando Modelos de Ensembles (Bosques y Boosting)...")
    
    # Random Forest
    rf_model = RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_metrics = {
        "mae": float(mean_absolute_error(y_test, rf_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
        "r2": float(r2_score(y_test, rf_pred))
    }

    # Extra Trees
    et_model = ExtraTreesRegressor(n_estimators=400, max_depth=15, random_state=42, n_jobs=-1)
    et_model.fit(X_train, y_train)
    et_pred = et_model.predict(X_test)
    et_metrics = {
        "mae": float(mean_absolute_error(y_test, et_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, et_pred))),
        "r2": float(r2_score(y_test, et_pred))
    }

    # Gradient Boosting
    gb_model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.03, max_depth=5, random_state=42)
    gb_model.fit(X_train, y_train)
    gb_pred = gb_model.predict(X_test)
    gb_metrics = {
        "mae": float(mean_absolute_error(y_test, gb_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, gb_pred))),
        "r2": float(r2_score(y_test, gb_pred))
    }

    # Mapeo de importancia de variables (Extra Trees)
    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": et_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    et_feature_importance = importance_df.to_dict(orient="records")

    # ==========================================================================
    # 4. PREPARACIÓN E INYECCIÓN A MONGODB (CON CAMBIO DE NOMBRE EXPLICITO)
    # ==========================================================================
    documento_avanzado = {
        "fecha_ejecucion": datetime.datetime.now(datetime.timezone.utc),
        "dataset_origen": INPUT_CSV_PATH.name,
        # Cambiamos explícitamente el nombre de la clave para la Red Neuronal:
        "red_neuronal_results": {
            "nombre": "Advanced PyTorch Deep Neural Network",
            "metricas": nn_metrics
        },
        "ensembles_results": {
            "random_forest": {"metricas": rf_metrics},
            "extra_trees": {
                "metricas": et_metrics,
                "feature_importance": et_feature_importance
            },
            "gradient_boosting": {"metricas": gb_metrics}
        }
    }

    print("🔌 Conectando a MongoDB Local (Docker)...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    print(f"📤 Inyectando analíticas avanzadas en '{COLLECTION_NAME}'...")
    result = collection.insert_one(documento_avanzado)

    print("🎉 ¡Inyección de modelos avanzados completada con éxito!")
    print(f"   → ID del documento: {result.inserted_id}")
    print(f"   → Mapeado bajo la clave clave: 'red_neuronal_results'")
    print(f"   📊 [PyTorch NN] R2: {nn_metrics['r2']:.4f}")
    print(f"   📊 [Extra Trees] R2: {et_metrics['r2']:.4f}")

except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado durante el proceso:")
    print(e)
    sys.exit(1)

print("Fin del script.")