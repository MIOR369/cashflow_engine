import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

def extract_features(df):
    df.columns = ["date","client","value"]

    total_revenue = df[df.value > 0]["value"].sum()
    clients = df.groupby("client")["value"].sum()

    worst_margin = clients.min()
    top_value = clients.max()

    dependency = (top_value / total_revenue) if total_revenue > 0 else 0
    volatility = df["value"].std()
    concentration = np.sum((clients / total_revenue)**2) if total_revenue > 0 else 0

    loss_clients = (clients < 0).sum()

    return [
        worst_margin,
        dependency,
        volatility,
        concentration,
        loss_clients,
        len(clients)
    ]

# ---- DATASET ----
X = []
y = []

for i in range(300):
    vals = np.random.normal(0, 500, 50)
    clients = np.random.choice(["A","B","C","D","E"], 50)

    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=50),
        "client": clients,
        "value": vals
    })

    features = extract_features(df)

    # 🔴 LABEL PROBABILISTICA CORRETTA
    score = 0

    if features[0] < -500:
        score += 0.4
    if features[2] > 400:
        score += 0.3
    if features[1] > 0.5:
        score += 0.3

    label = 1 if np.random.rand() < score else 0

    X.append(features)
    y.append(label)

# ---- TRAIN ----
model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("MODEL TRAINED OK")
