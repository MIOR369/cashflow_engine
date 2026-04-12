from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
import subprocess
import json
import os

app = Flask(__name__)

# ======================
# CONFIG
# ======================
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "super-secret")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# ======================
# DB
# ======================
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager(app)

# ======================
# USER MODEL
# ======================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ======================
# HOME (CRITICO)
# ======================
@app.route("/")
def home():
    return render_template("index.html")

# ======================
# REGISTER
# ======================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        file = request.files['file']

        file_path = "input.csv"
        file.save(file_path)

        normalized_path = normalize_csv(file_path)

        import subprocess
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

        import json
        return jsonify(json.loads(result.stdout))

    except Exception as e:
        return jsonify({
            "status": "error",
            "msg": str(e)
        })

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json

        user = User.query.filter_by(
            username=data.get("username"),
            password=data.get("password")
        ).first()

        if user:
            login_user(user)
            return {"status": "ok"}

        return {"status": "error"}, 401

    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500

# ======================
# ANALYZE
# ======================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        if "file" not in request.files:
            return {"status": "error", "msg": "no file"}, 400

        file = request.files["file"]
        file_path = "data.csv"
        file.save(file_path)
    normalized_path = normalize_csv(file_path)

        result = subprocess.run(
            ["./cashflow", file_path, "1000"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "msg": "engine failed",
                "stderr": result.stderr
            }, 500

        if not os.path.exists("output.json"):
            return {"status": "error", "msg": "no output"}, 500

        with open("output.json") as f:
            data = json.load(f)

        return jsonify(data)

    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500

# ======================
# HEALTH CHECK
# ======================
@app.route("/healthz")
def health():
    return {"status": "ok"}

# ======================
# RUN (RENDER)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

# === CSV UNIVERSALE NORMALIZER ===
import pandas as pd

def normalize_csv(file_path):
    df = pd.read_csv(file_path)

    col_map = {}

    for col in df.columns:
        c = col.lower()

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

