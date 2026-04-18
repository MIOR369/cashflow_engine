from pro_parser_patch import normalize_csv
from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# -------------------------
# ENGINE
# -------------------------
def run_engine(df):

    total_loss = float(df[df["value"] < 0]["value"].sum())
    total_positive = float(df[df["value"] > 0]["value"].sum())

    clients = df.groupby("client")["value"].sum()

    worst_client = str(clients.idxmin())
    worst_value = float(clients.min())

    dependency = float((clients.max() / total_positive) * 100) if total_positive > 0 else 0
    volatility = float(df["value"].std())
    concentration = float(sum((clients / total_positive) ** 2)) if total_positive > 0 else 0

    prob = 0.71

    # 🔴 FIX: VALORE REALE 90 GIORNI
    loss_90d = abs(total_loss) * 3

    impact = f"SE NON AGISCI → perdi €{int(loss_90d)} entro 3 mesi"

    losses = []

    ineff = abs(total_loss) * 0.5
    losses.append({
        "name": "Inefficienza operativa",
        "loss": float(ineff),
        "action": "Aumenta produttività o riduci costi"
    })

    for client, val in clients.items():
        if val < 0:
            losses.append({
                "name": f"Cliente {client}",
                "loss": float(abs(val)),
                "action": f"Rinegozia o elimina cliente {client}"
            })

    total_loss_abs = abs(total_loss)
    raw_sum = sum(x["loss"] for x in losses)

    if raw_sum > 0:
        for x in losses:
            x["loss"] = float((x["loss"] / raw_sum) * total_loss_abs)

    for x in losses:
        x["percent"] = float((x["loss"] / total_loss_abs) * 100) if total_loss_abs > 0 else 0

    ranked = sorted(losses, key=lambda x: x["loss"], reverse=True)
    top_actions = ranked[:3]

    for x in top_actions:
        x["monthly_gain"] = float(x["loss"] * 3)
        x["annual_gain"] = float(x["monthly_gain"] * 12)

    total_annual_gain = float(sum(x["annual_gain"] for x in top_actions))

    return {
        "probability": float(prob),

        "loss_90d": float(loss_90d),  # 🔴 FIX CRITICO

        "economic": {
            "total_loss": float(total_loss),
            "recoverable": float(abs(total_loss))
        },

        "clients": {
            "critical": worst_client,
            "worst_margin": float(worst_value)
        },

        "structure": {
            "dependency": float(dependency),
            "volatility": float(volatility),
            "concentration": float(concentration)
        },

        "impact": str(impact),

        "top_actions": top_actions,
        "total_annual_gain": float(total_annual_gain)
    }

# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files["file"]

        if not file:
            return jsonify({"error": "No file"}), 400

        file_path = "input.csv"
        file.save(file_path)

        df = normalize_csv(file_path)   # ✅ QUESTO È IL FIX
        result = run_engine(df)

        return jsonify(result)

    except Exception as e:
        print("ERRORE:", str(e))
        return jsonify({"error": str(e)}), 500

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
