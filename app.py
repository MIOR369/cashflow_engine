from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os
import pandas as pd

app = Flask(__name__)

# === CSV UNIVERSALE NORMALIZER ===
def normalize_csv(file_path):
    df = pd.read_csv(file_path)

    # 🔴 FIX: CSV senza header
    if df.columns.tolist() == [0,1,2]:
        df.columns = ["date", "client", "value"]

    col_map = {}

    for col in df.columns:
        c = str(col).lower()

        if "date" in c or "data" in c:
            col_map[col] = "date"
        elif "client" in c or "cliente" in c or "name" in c:
            col_map[col] = "client"
        elif "amount" in c or "value" in c or "valore" in c:
            col_map[col] = "value"

    df = df.rename(columns=col_map)

    if not all(k in df.columns for k in ["date", "client", "value"]):
        raise Exception("Formato CSV non valido")

    df = df[["date", "client", "value"]]

    temp_path = "normalized.csv"
    df.to_csv(temp_path, index=False, header=False)

    return temp_path


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
            ["./cashflow", normalized_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "msg": "engine failed",
                "stderr": result.stderr
            })

        return jsonify(json.loads(result.stdout))

    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": str(e)
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
