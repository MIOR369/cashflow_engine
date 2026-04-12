from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os
import pandas as pd

app = Flask(__name__)

# === AUTO BUILD (CRITICO PER RENDER) ===
if not os.path.exists("cashflow"):
    subprocess.run([
        "g++", "main.cpp",
        "parser.cpp",
        "simulator.cpp",
        "simulator_prob.cpp",
        "delay_engine.cpp",
        "multi_cause_engine.cpp",
        "impact_engine.cpp",
        "date_utils.cpp",
        "delay_utils.cpp",
        "risk_engine.cpp",
        "decision_engine.cpp",
        "advice_engine.cpp",
        "scenario_engine.cpp",
        "optimizer_engine.cpp",
        "structure_engine.cpp",
        "execution_engine.cpp",
        "margin.cpp",
        "final_engine.cpp",
        "-O3", "-std=c++17",
        "-o", "cashflow"
    ])

    os.chmod("cashflow", 0o755)


# === CSV UNIVERSALE ===
def normalize_csv(file_path):
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

        try:
            return jsonify(json.loads(result.stdout))
        except:
            return jsonify({"raw": result.stdout})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
