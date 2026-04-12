from flask import Flask, request, jsonify, render_template
import subprocess
import os
import pandas as pd
import re

app = Flask(__name__)

# === CSV PARSER UNIVERSALE ===
def normalize_csv(file_path):
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path, sep=None, engine='python')

    df.columns = [str(c).strip().lower() for c in df.columns]

    date_col = None
    client_col = None
    value_col = None

    for col in df.columns:
        if not date_col and re.search(r'date|data|giorno', col):
            date_col = col
        elif not client_col and re.search(r'client|customer|cliente|name', col):
            client_col = col
        elif not value_col and re.search(r'value|amount|importo|ricavo|€', col):
            value_col = col

    if not date_col or not client_col or not value_col:
        cols = df.columns.tolist()
        if len(cols) < 3:
            raise Exception("Formato CSV non valido")
        date_col, client_col, value_col = cols[:3]

    df = df[[date_col, client_col, value_col]].copy()
    df.columns = ["date", "client", "value"]

    df["value"] = (
        df["value"]
        .astype(str)
        .str.replace(",", ".")
        .str.replace(r"[^\d\.-]", "", regex=True)
    )

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    temp_path = "normalized.csv"
    df.to_csv(temp_path, index=False, header=False)

    return temp_path

# ✅ FIX CRITICO QUI
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "msg": "no file"})

        file = request.files['file']

        file_path = "input.csv"
        file.save(file_path)

        normalized_path = normalize_csv(file_path)

        result = subprocess.run(
            ["./cashflow", normalized_path, "1000"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "msg": "engine failed",
                "stderr": result.stderr
            })

        output = result.stdout

        risk = re.search(r'RISK:\s*([\d\.]+)%', output)
        margin = re.search(r'CLIENT MARGIN:\s*(-?\d+)', output)
        client = re.search(r'CRITICAL CLIENT:\s*(\w+)', output)
        diagnosis = re.search(r'DIAGNOSIS:\s*(.*)', output)
        action = re.search(r'ACTION:\s*(.*)', output)

        return jsonify({
            "risk": float(risk.group(1)) if risk else None,
            "margin": int(margin.group(1)) if margin else None,
            "critical_client": client.group(1) if client else None,
            "diagnosis": diagnosis.group(1) if diagnosis else None,
            "action": action.group(1) if action else None
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": str(e)
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
