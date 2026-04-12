from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_sqlalchemy import SQLAlchemy
import subprocess
import json

app = Flask(__name__)

# CONFIG
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# DB
db = SQLAlchemy(app)

# INIT DB (Flask 3 FIX)
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
    return User.query.get(int(user_id))

# ======================
# REGISTER
# ======================
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    user = User(
        username=data["username"],
        password=data["password"]
    )

    db.session.add(user)
    db.session.commit()

    return {"status": "created"}

# ======================
# LOGIN
# ======================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(
        username=data["username"],
        password=data["password"]
    ).first()

    if user:
        login_user(user)
        return {"status": "ok"}

    return {"status": "error"}, 401

# ======================
# ANALYZE (PROTECTED)
# ======================
@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["file"]
    file.save("data.csv")

    subprocess.run(["./cashflow", "data.csv", "1000"])

    with open("output.json") as f:
        data = json.load(f)

    return jsonify(data)

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(port=5001)
