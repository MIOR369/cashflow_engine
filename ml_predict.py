import pandas as pd
import numpy as np
import joblib
import sys
import json

model = joblib.load("model.pkl")

file = sys.argv[1]

df = pd.read_csv(file, header=None)
df.columns = ["date","client","value"]

# ---- FEATURE ENGINEERING ----
total_revenue = df[df.value > 0]["value"].sum()
clients = df.groupby("client")["value"].sum()

worst_margin = clients.min()
top_value = clients.max()

dependency = (top_value / total_revenue) if total_revenue > 0 else 0
volatility = df["value"].std()
concentration = np.sum((clients / total_revenue)**2) if total_revenue > 0 else 0
loss_clients = (clients < 0).sum()

features = [[
    worst_margin,
    dependency,
    volatility,
    concentration,
    loss_clients,
    len(clients)
]]

# ---- PREDICTION ----
pred = model.predict(features)[0]
prob = model.predict_proba(features)[0][1]

# ---- OUTPUT JSON CORRETTO ----
print(json.dumps({
    "prediction": int(pred),
    "failure_probability": float(prob)
}))
