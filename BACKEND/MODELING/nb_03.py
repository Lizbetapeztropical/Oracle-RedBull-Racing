
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path

from torch.utils.data import TensorDataset, DataLoader

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


import matplotlib.pyplot as plt

print("1")
import pandas as pd

print("2")
import numpy as np

print("3")
import torch

print("4")
import torch.nn as nn

print("5")

if __name__ == "__main__":
    # Cargar datos desde la ruta correcta
    CSV_PATH = Path("BACKEND/RAWDATA/DATA/Merged/merged_dataset.csv")
    
    print("📂 Cargando archivo merged_dataset.csv...")
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")


print("6")


# ============================================================
# F1 DEEP LEARNING MODEL
# ============================================================

class F1NeuralNetwork(nn.Module):

    def __init__(self, input_size):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.30),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.30),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.20),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 1)
        )

    def forward(self, x):

        return self.network(x)


# ============================================================
# TRAIN FUNCTION
# ============================================================

def train_f1_neural_network(df):

    # ============================================================
    # FEATURES
    # ============================================================

    features = [
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

    # ============================================================
    # CLEAN DATA
    # ============================================================

    model_df = df[features + [target]].copy()

    model_df = model_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    model_df = model_df.dropna()

    X = model_df[features]
    y = model_df[target].values

    # ============================================================
    # TRAIN TEST SPLIT
    # ============================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    # ============================================================
    # SCALING
    # ============================================================

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ============================================================
    # TENSORS
    # ============================================================

    X_train_tensor = torch.tensor(
        X_train_scaled,
        dtype=torch.float32
    )

    X_test_tensor = torch.tensor(
        X_test_scaled,
        dtype=torch.float32
    )

    y_train_tensor = torch.tensor(
        y_train,
        dtype=torch.float32
    ).view(-1, 1)

    y_test_tensor = torch.tensor(
        y_test,
        dtype=torch.float32
    ).view(-1, 1)

    # ============================================================
    # DEVICE
    # ============================================================

    device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    # ============================================================
    # DATASET
    # ============================================================

    train_dataset = TensorDataset(
        X_train_tensor,
        y_train_tensor
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=32,
        shuffle=True
    )

    # ============================================================
    # MODEL
    # ============================================================

    model = F1NeuralNetwork(
        input_size=len(features)
    ).to(device)

    criterion = nn.MSELoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=0.001,
        weight_decay=1e-5
    )

    # ============================================================
    # TRAINING
    # ============================================================

    epochs = 300

    losses = []

    for epoch in range(epochs):

        model.train()

        running_loss = 0

        for batch_X, batch_y in train_loader:

            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()

            predictions = model(batch_X)

            loss = criterion(
                predictions,
                batch_y
            )

            loss.backward()

            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)

        losses.append(epoch_loss)

        if (epoch + 1) % 25 == 0:

            print(
                f"Epoch [{epoch+1}/{epochs}] "
                f"Loss: {epoch_loss:.4f}"
            )

    # ============================================================
    # EVALUATION
    # ============================================================

    model.eval()

    with torch.no_grad():

        y_pred = model(
            X_test_tensor.to(device)
        )

    y_pred = (
        y_pred.cpu()
        .numpy()
        .flatten()
    )

    metrics = {

        "MAE": mean_absolute_error(
            y_test,
            y_pred
        ),

        "RMSE": np.sqrt(
            mean_squared_error(
                y_test,
                y_pred
            )
        ),

        "R2": r2_score(
            y_test,
            y_pred
        )
    }

    # ============================================================
    # FEATURE IMPORTANCE (PERMUTATION STYLE)
    # ============================================================

    print("\nModel Metrics")
    print(metrics)

    return {
    "model": model,
    "scaler": scaler,
    "features": features,
    "metrics": metrics,
    "losses": losses,
    "X_test": X_test,
    "y_test": y_test,
    "predictions": y_pred
}


# ============================================================
# TRAIN MODEL
# ============================================================

results_torch = train_f1_neural_network(df)

# ============================================================
# SAVE MODEL
# ============================================================

torch.save(
    results_torch["model"].state_dict(),
    "f1_neural_network.pth"
)

# ============================================================
# SAVE OBJECTS
# ============================================================

import pickle

with open("f1_scaler.pkl", "wb") as f:
    pickle.dump(
        results_torch["scaler"],
        f
    )

with open("f1_features.pkl", "wb") as f:
    pickle.dump(
        results_torch["features"],
        f
    )

with open("f1_metrics.pkl", "wb") as f:
    pickle.dump(
        results_torch["metrics"],
        f
    )

# ============================================================
# PREDICTIONS DATAFRAME
# ============================================================

prediction_df_torch = pd.DataFrame({

    "Actual_SCORE":
        results_torch["y_test"],

    "Predicted_SCORE":
        results_torch["predictions"],

    "Error":
        np.abs(
            results_torch["y_test"]
            -
            results_torch["predictions"]
        )

})

# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_df_torch.to_pickle(
    "f1_predictions.pkl"
)

prediction_df_torch.to_csv(
    "f1_predictions.csv",
    index=False
)

print("Saved:")
print(" - f1_neural_network.pth")
print(" - f1_scaler.pkl")
print(" - f1_features.pkl")
print(" - f1_metrics.pkl")
print(" - f1_predictions.pkl")
print(" - f1_predictions.csv")