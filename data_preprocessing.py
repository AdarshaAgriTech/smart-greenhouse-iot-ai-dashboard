import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

# =====================================
# LOAD DATASET
# =====================================

df = pd.read_excel(
    "Hourly EC and pH temeperature relative humidity data.xlsx"
)

# =====================================
# COMBINE DATE + TIME
# =====================================

df["timestamp"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Time"].astype(str)
)

# =====================================
# REMOVE MISSING VALUES
# =====================================

df = df.dropna()

# =====================================
# SORT BY TIME
# =====================================

df = df.sort_values("timestamp")

# =====================================
# TIME FEATURES
# =====================================

df["hour"] = df["timestamp"].dt.hour

df["day"] = df["timestamp"].dt.day

df["month"] = df["timestamp"].dt.month

# =====================================
# LAG FEATURES
# =====================================

df["temp_lag_1"] = df[
    "Hourly average temperature (°C)"
].shift(1)

df["rh_lag_1"] = df[
    "Hourly average relative humidity (%)"
].shift(1)

# =====================================
# ROLLING AVERAGES
# =====================================

df["temp_rolling_mean"] = df[
    "Hourly average temperature (°C)"
].rolling(window=3).mean()

df["rh_rolling_mean"] = df[
    "Hourly average relative humidity (%)"
].rolling(window=3).mean()

# =====================================
# REMOVE NEW NaN ROWS
# =====================================

df = df.dropna()

# =====================================
# DISPLAY CLEAN DATA
# =====================================

print("\nCLEANED DATA\n")

print(df.head())

print("\nDATASET SHAPE\n")

print(df.shape)

# =====================================
# SAVE CLEANED DATASET
# =====================================

df.to_csv(
    "cleaned_greenhouse_data.csv",
    index=False
)

print("\nCleaned dataset saved successfully.")

# =====================================
# FEATURES
# =====================================

X = df[[
    "hour",
    "temp_lag_1",
    "rh_lag_1",
    "temp_rolling_mean",
    "rh_rolling_mean"
]]

# =====================================
# TARGET
# =====================================

y = df["Hourly average relative humidity (%)"]

# =====================================
# TRAIN TEST SPLIT
# =====================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =====================================
# MODEL
# =====================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

# SAVE TRAINED MODEL

joblib.dump(
    model,
    "humidity_prediction_model.pkl"
)

print("\nModel saved successfully.")

# =====================================
# PREDICTION
# =====================================

y_pred = model.predict(X_test)

# =====================================
# EVALUATION METRICS
# =====================================

r2 = r2_score(y_test, y_pred)

mae = mean_absolute_error(y_test, y_pred)

rmse = np.sqrt(
    mean_squared_error(y_test, y_pred)
)

print("\nR2 SCORE\n")
print(round(r2, 3))

print("\nMAE\n")
print(round(mae, 3))

print("\nRMSE\n")
print(round(rmse, 3))

# =====================================
# ACTUAL VS PREDICTED GRAPH
# =====================================

plt.figure(figsize=(10,5))

plt.plot(
    y_test.values,
    label="Actual RH"
)

plt.plot(
    y_pred,
    label="Predicted RH"
)

plt.xlabel("Test Samples")

plt.ylabel("Relative Humidity (%)")

plt.title("Actual vs Predicted RH")

plt.legend()

plt.grid(True)

plt.show()

# =====================================
# FUTURE PREDICTION
# =====================================

latest_data = X.iloc[-1:]

future_rh = model.predict(latest_data)

print("\nPREDICTED NEXT HOUR RELATIVE HUMIDITY\n")

print(round(future_rh[0], 2), "%")

# =====================================
# FEATURE IMPORTANCE
# =====================================

importance_df = pd.DataFrame({

    "Feature": X.columns,

    "Importance": model.feature_importances_
})

importance_df = importance_df.sort_values(
    "Importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE\n")

print(importance_df)