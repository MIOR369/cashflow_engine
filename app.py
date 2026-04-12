from flask import Flask, request, jsonify, render_template
import subprocess
import json
import os
import pandas as pd

app = Flask(__name__)

# === CSV UNIVERSALE NORMALIZER ===
def normalize_csv(file_path):
    import pandas as pd

    # 🔴 LEGGE SEMPRE SENZA HEADER
    df = pd.read_csv(file_path, header=None)

    # 🔴 FORZA STRUTTURA
    if df.shape[1] < 3:
        raise Exception("Formato CSV non valido")

    df = df.iloc[:, :3]
    df.columns = ["date", "client", "value"]

    temp_path = "normalized.csv"
    df.to_csv(temp_path, index=False, header=False)

    return temp_path

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
