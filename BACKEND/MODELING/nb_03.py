#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import TensorDataset, DataLoader

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

import matplotlib.pyplot as plt


# In[ ]:


#df = pd.read_csv("processed_dataset.csv")


# In[ ]:


# ============================================================
# ADVANCED PYTORCH + ENSEMBLE MODELS
# ============================================================


# ============================================================
# FEATURES & TARGET
# ============================================================

features = [
    "POINTS",
    "LAPS",
    "MILLISECONDS",
    "WEATHER_cloudy",
    "OVERTAKEN_POSITIONS_TOTAL",
    "DNF_COUNT",
    "LAPMEAN",
    "PS_COUNT",
    "SC_COUNT",
    "DRIVER_ENCODED",
    "RACE_ENCODED"
]

target = "SCORE"

# ============================================================
# CLEAN DATA
# ============================================================

model_df = df[features + [target]].copy()

model_df = model_df.replace([np.inf, -np.inf], np.nan)
model_df = model_df.dropna()

X = model_df[features]
y = model_df[target].values

# ============================================================
# TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ============================================================
# FEATURE SCALING
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# PYTORCH TENSORS
# ============================================================

X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)

y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1,1)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1,1)

# ============================================================
# DATALOADER
# ============================================================

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)

# ============================================================
# ADVANCED PYTORCH MODEL
# ============================================================

class F1NeuralNetwork(nn.Module):

    def __init__(self, input_size):
        super(F1NeuralNetwork, self).__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.40),

            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.35),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.30),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, 1) # Output layer for regression, no activation
        )

    def forward(self, x):
        return self.network(x)

# ============================================================
# INITIALIZE MODEL
# ============================================================

input_size = X_train.shape[1]

model = F1NeuralNetwork(input_size)

# ============================================================
# LOSS + OPTIMIZER
# ============================================================

criterion = nn.MSELoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001,
    weight_decay=1e-5
)

# ============================================================
# CUDA DEVICE SETUP (Integrated into this cell)
# ============================================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Move model to the device
model.to(device)

# Move tensors to the device. Note: DataLoader will pick up these device-moved tensors.
X_train_tensor = X_train_tensor.to(device)
X_test_tensor = X_test_tensor.to(device)
y_train_tensor = y_train_tensor.to(device)
y_test_tensor = y_test_tensor.to(device)

# Re-create DataLoader to ensure tensors are on the correct device if they were not already
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)

# ============================================================
# TRAINING
# ============================================================

epochs = 300 # Changed to 300 epochs as requested

losses = []

for epoch in range(epochs):

    model.train()

    running_loss = 0

    for batch_X, batch_y in train_loader:
        # Ensure batch_X and batch_y are on the correct device (already moved)
        optimizer.zero_grad()

        predictions = model(batch_X)

        loss = criterion(predictions, batch_y)

        loss.backward()

        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)

    losses.append(avg_loss)

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{epochs}] | Loss: {avg_loss:.4f}")

# ============================================================
# PREDICTIONS
# ============================================================

model.eval()

with torch.no_grad():

    y_pred_tensor = model(X_test_tensor)

y_pred_nn = y_pred_tensor.cpu().numpy().flatten() # Move to CPU before numpy conversion

# ============================================================
# NN METRICS
# ============================================================

nn_mae = mean_absolute_error(y_test, y_pred_nn)
nn_rmse = np.sqrt(mean_squared_error(y_test, y_pred_nn))
nn_r2 = r2_score(y_test, y_pred_nn)

print("\n========== PYTORCH NN RESULTS ==========")
print(f"MAE  : {nn_mae:.4f}")
print(f"RMSE : {nn_rmse:.4f}")
print(f"R2   : {nn_r2:.4f}")

# ============================================================
# RANDOM FOREST
# ============================================================

rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=12,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)

rf_mae = mean_absolute_error(y_test, rf_pred)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_r2 = r2_score(y_test, rf_pred)

print("\n========== RANDOM FOREST RESULTS ==========")
print(f"MAE  : {rf_mae:.4f}")
print(f"RMSE : {rf_rmse:.4f}")
print(f"R2   : {rf_r2:.4f}")

# ============================================================
# EXTRA TREES
# ============================================================

et_model = ExtraTreesRegressor(
    n_estimators=400,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

et_model.fit(X_train, y_train)

et_pred = et_model.predict(X_test)

et_mae = mean_absolute_error(y_test, et_pred)
et_rmse = np.sqrt(mean_squared_error(y_test, et_pred))
et_r2 = r2_score(y_test, et_pred)

print("\n========== EXTRA TREES RESULTS ==========")
print(f"MAE  : {et_mae:.4f}")
print(f"RMSE : {et_rmse:.4f}")
print(f"R2   : {et_r2:.4f}")

# ============================================================
# GRADIENT BOOSTING
# ============================================================

gb_model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.03,
    max_depth=5,
    random_state=42
)

gb_model.fit(X_train, y_train)

gb_pred = gb_model.predict(X_test)

gb_mae = mean_absolute_error(y_test, gb_pred)
gb_rmse = np.sqrt(mean_squared_error(y_test, gb_pred))
gb_r2 = r2_score(y_test, gb_pred)

print("\n========== GRADIENT BOOSTING RESULTS ==========")
print(f"MAE  : {gb_mae:.4f}")
print(f"RMSE : {gb_rmse:.4f}")
print(f"R2   : {gb_r2:.4f}")

# ============================================================
# FINAL MODEL COMPARISON
# ============================================================

comparison = pd.DataFrame({
    "Model": [
        "PyTorch Neural Network",
        "Random Forest",
        "Extra Trees",
        "Gradient Boosting"
    ],
    "MAE": [
        nn_mae,
        rf_mae,
        et_mae,
        gb_mae
    ],
    "RMSE": [
        nn_rmse,
        rf_rmse,
        et_rmse,
        gb_rmse
    ],
    "R2": [
        nn_r2,
        rf_r2,
        et_r2,
        gb_r2
    ]
})

comparison = comparison.sort_values(
    by="R2",
    ascending=False
)

print("\n========== FINAL MODEL COMPARISON ==========")
print(comparison)

# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": et_model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)


print("\n========== FEATURE IMPORTANCE ==========")
print(importance_df)

# ============================================================
# LOSS CURVE
# ============================================================

plt.figure(figsize=(10,5))

plt.plot(losses)

plt.title("PyTorch Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")

plt.show()

# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "Actual_SCORE": y_test,
    "Predicted_SCORE": y_pred_nn
})

print("\n========== SAMPLE PREDICTIONS ==========")
print(results.head(10))

# ============================================================
# SAVE ALL MODELS AS PICKLES
# ============================================================

import pickle

# Random Forest
with open("random_forest.pkl", "wb") as f:
    pickle.dump(rf_model, f)

# Extra Trees
with open("extra_trees.pkl", "wb") as f:
    pickle.dump(et_model, f)

# Gradient Boosting
with open("gradient_boosting.pkl", "wb") as f:
    pickle.dump(gb_model, f)

# Scaler
with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Features list
with open("features.pkl", "wb") as f:
    pickle.dump(features, f)

print("All sklearn models saved as pickle.")

with open("f1_pytorch_model.pkl", "wb") as f:
    pickle.dump(model.cpu(), f)

print("PyTorch model saved as pickle.")
