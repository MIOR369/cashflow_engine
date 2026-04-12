from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os
import pandas as pd

app = Flask(__name__)

# === CSV UNIVERSALE ===
def normalize_csv(file_path):
    # prova più separatori
    for sep in [",", ";", "\t", "|"]:
        try:
            df = pd.read_csv(file_path, sep=sep, header=None, engine="python")
            if df.shape[1] >= 3:
                break
        except:
            continue
    else:
        raise Exception("Formato CSV non valido")

    df = df.iloc[:, :3]
    df.columns = ["date", "client", "value"]

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()

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

        # prova JSON diretto
        try:
            return jsonify(json.loads(result.stdout))
        except:
            return jsonify({"raw": result.stdout})

    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": str(e)
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
