#!/usr/bin/env python
# coding: utf-8

# In[2]:


# ============================================
# MLP REGRESSION - PREDICTING SCORE
# ============================================

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import joblib

#df = pd.read_csv("processed_dataset.csv")

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
    "SC_COUNT",
    "DRIVER_ENCODED",
    "RACE_ENCODED"
]

target = "SCORE"

# ============================================
# CREATE CLEAN DATAFRAME
# ============================================

model_df = df[features + [target]].copy()

# replace inf values
model_df = model_df.replace([np.inf, -np.inf], np.nan)

# remove missing rows
model_df = model_df.dropna()

# ============================================
# X AND y
# ============================================

X = model_df[features]

# make y 1D
y = model_df[target].values.ravel()

# ============================================
# TRAIN / TEST SPLIT
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

# IMPORTANT:
# Neural networks also need scaling

mlp_model = Pipeline([
    ("scaler", StandardScaler()),

    ("mlp", MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),  # architecture
        activation="relu",
        solver="adam",
        alpha=0.0001,        # regularization
        learning_rate="adaptive",
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1
    ))
])

# ============================================
# TRAIN MODEL
# ============================================

mlp_model.fit(X_train, y_train)

# ============================================
# PREDICTIONS
# ============================================

y_pred = mlp_model.predict(X_test)

# ============================================
# EVALUATION
# ============================================

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("========== MLP RESULTS ==========")
print(f"MAE  : {mae:.4f}")
print(f"RMSE : {rmse:.4f}")
print(f"R2   : {r2:.4f}")

# ============================================
# SAMPLE PREDICTIONS
# ============================================

results = pd.DataFrame({
    "Actual_SCORE": y_test,
    "Predicted_SCORE": y_pred
})

print("\nSample predictions:")
print(results.head(10))

# ============================================
# OPTIONAL: SAVE MODEL
# ============================================

joblib.dump(mlp_model, "mlp_score_model.pkl")

print("\nModel saved as mlp_score_model.pkl")


# In[ ]:




