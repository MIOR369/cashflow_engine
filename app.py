from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import subprocess, json, os, re, time, hashlib
import pandas as pd
import stripe

# ======================
# INIT
# ======================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(app, supports_credentials=True)

db = SQLAlchemy(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
login_manager = LoginManager(app)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# ======================
# MODELS
# ======================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    access_level = db.Column(db.Integer, default=0)
    token = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.Float, default=time.time)

# ======================
# AUTH
# ======================

def generate_token(user):
    return hashlib.sha256(f"{user.id}-{user.email}-diagn-eco-2026".encode()).hexdigest()

def get_user_from_token(token):
    if not token:
        return None
    return User.query.filter_by(token=token).first()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ======================
# CSV
# ======================

def clean_value(s):
    s = s.strip().strip('"').strip("'")
    s = re.sub(r"[€\s]", "", s)
    s = s.replace(",", ".")
    return s

def normalize_csv(file_path):
    rows = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = [p.strip() for p in line.replace(";", ",").split(",")]
            if len(parts) < 3:
                continue

            try:
                value = float(clean_value(parts[2]))
                rows.append([parts[0], parts[1], value])
            except:
                continue

    if not rows:
        raise Exception("CSV non valido")

    df = pd.DataFrame(rows)
    df.to_csv("normalized.csv", index=False, header=False)
    return "normalized.csv"

# ======================
# FILTER
# ======================

def filter_output(data, level):
    if level == 0:
        return {
            "loss_90d": data.get("loss_90d", 0),
            "recovery_potential": data.get("recovery_potential", 0),
            "locked": True
        }
    elif level == 1:
        return {
            "loss_90d": data.get("loss_90d", 0),
            "recovery_potential": data.get("recovery_potential", 0),
            "top_losses": data.get("top_losses", []),
            "locked": False
        }
    else:
        data["locked"] = False
        return data

# ======================
# ROUTES
# ======================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if "@" not in email:
        return {"error": "invalid email"}, 400

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    user.token = generate_token(user)
    db.session.commit()

    login_user(user)

    return {"token": user.token, "access_level": user.access_level}

@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    if "file" not in request.files:
        return {"error": "no file"}, 400

    f = request.files["file"]
    f.save("data.csv")

    normalized = normalize_csv("data.csv")

    result = subprocess.run(
        ["./cashflow", normalized, "1000"],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        return {"error": "engine failed", "stderr": result.stderr}, 500

    try:
        data = json.loads(result.stdout)
    except:
        return {"error": "invalid engine output"}, 500

    token = request.headers.get("X-User-Token")
    user = get_user_from_token(token)

    level = user.access_level if user else 0

    return jsonify(filter_output(data, level))

# ======================
# CHECKOUT
# ======================

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout():

    data = request.get_json(silent=True) or {}
    tier = data.get("tier")

    token = request.headers.get("X-User-Token")
    user = get_user_from_token(token)

    if not user:
        return {"error": "non autenticato"}, 401

    price_map = {
        "base": os.environ.get("STRIPE_PRICE_BASE"),
        "full": os.environ.get("STRIPE_PRICE_FULL")
    }

    price_id = price_map.get(tier)

    if not price_id:
        return {"error": "invalid tier or missing price"}, 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=os.environ.get("BASE_URL") + "/success",
            cancel_url=os.environ.get("BASE_URL") + "/",
            metadata={"user_id": user.id, "tier": tier}
        )

        return {"url": session.url}

    except Exception as e:
        return {"error": str(e)}, 500

# ======================
# WEBHOOK
# ======================

@app.route("/webhook", methods=["POST"])
def webhook():

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
    except:
        return {"error": "invalid webhook"}, 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        user = db.session.get(User, int(session["metadata"]["user_id"]))
        tier = session["metadata"]["tier"]

        if user:
            user.access_level = 1 if tier == "base" else 2
            db.session.commit()

    return {"status": "ok"}

# ======================
# HEALTH
# ======================

@app.route("/healthz")
def health():
    return {"status": "ok"}

# ======================
# RUN
# ======================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
