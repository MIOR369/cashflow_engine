from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import subprocess, json, os, re, time, hashlib
import pandas as pd
try:
    import stripe
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
except:
    stripe = None

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "diagn-eco-secret-2026")
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

STRIPE_PRICE_BASE = os.environ.get("STRIPE_PRICE_BASE", "price_1TNbey7LfLS2sAiM4rs56ZCO")
STRIPE_PRICE_FULL = os.environ.get("STRIPE_PRICE_FULL", "price_1TNbez7LfLS2sAiMzpKdvfKt")
BASE_URL = os.environ.get("BASE_URL", "https://diagn-eco.onrender.com")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "admin-secret-local")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_44d26507c1cfbba953532e2ff2952878588a00063f3f8e986c982835a8f2e510")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    access_level = db.Column(db.Integer, default=0)
    token = db.Column(db.String(128), unique=True)
    created_at = db.Column(db.Float, default=time.time)

with app.app_context():
    db.create_all()
    owner = User.query.filter_by(email="ratiomoralis@gmail.com").first()
    if not owner:
        owner = User(email="ratiomoralis@gmail.com", access_level=2)
        db.session.add(owner)
    else:
        owner.access_level = 2
    db.session.commit()

def generate_token(user):
    return hashlib.sha256(f"{user.id}-{user.email}-diagn-eco-2026".encode()).hexdigest()

def get_user_from_token(token):
    if not token:
        return None
    return User.query.filter_by(token=token).first()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def clean_value(s):
    s = s.strip().strip('"').strip("'")
    s = re.sub(r"[€\s]", "", s)
    parts = s.split(".")
    if len(parts) > 1 and len(parts[-1]) != 2:
        s = "".join(parts)
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
    pd.DataFrame(rows).to_csv("normalized.csv", index=False, header=False)
    return "normalized.csv"

def filter_output(data, level):
    if level == 0:
        return {"access_level": 0, "diagnosis": data.get("diagnosis",""), "risk_score": data.get("risk_score",0), "loss_90d": data.get("loss_90d",0), "recovery_potential": data.get("recovery_potential",0), "locked": True}
    elif level == 1:
        return {"access_level": 1, "diagnosis": data.get("diagnosis",""), "action": data.get("action",""), "risk_score": data.get("risk_score",0), "loss_90d": data.get("loss_90d",0), "recovery_potential": data.get("recovery_potential",0), "worst_client": data.get("worst_client",""), "worst_margin": data.get("worst_margin",0), "best_client": data.get("best_client",""), "best_margin": data.get("best_margin",0), "total_margin": data.get("total_margin",0), "loss_annual": data.get("loss_annual",0), "top_losses": data.get("top_losses",[]), "locked": False}
    else:
        data["access_level"] = 2
        data["locked"] = False
        return data

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    if "@" not in email:
        return {"status": "error", "msg": "email non valida"}, 400
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()
    user.token = generate_token(user)
    db.session.commit()
    login_user(user)
    return {"status": "ok", "token": user.token, "access_level": user.access_level, "email": user.email}

@app.route("/me")
def me():
    token = request.headers.get("X-User-Token")
    user = get_user_from_token(token)
    if user:
        return {"status": "ok", "token": user.token, "access_level": user.access_level, "email": user.email}
    return {"status": "anonymous", "access_level": 0}

@app.route("/logout")
def logout():
    from flask_login import logout_user
    logout_user()
    return {"status": "ok"}

@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    if "file" not in request.files:
        return {"status": "error", "msg": "no file"}, 400
    request.files["file"].save("data.csv")
    try:
        normalized = normalize_csv("data.csv")
    except Exception as e:
        return {"status": "error", "msg": str(e)}, 400
    bin_path = "./cashflow" if os.path.exists("./cashflow") else "/opt/render/project/src/cashflow"
    result = subprocess.run([bin_path, normalized, "1000"], capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return {"status": "error", "msg": "engine failed", "stderr": result.stderr}, 500
    try:
        data = json.loads(result.stdout)
    except:
        return {"status": "error", "msg": "invalid output"}, 500
    token = request.headers.get("X-User-Token")
    user = get_user_from_token(token)
    return jsonify(filter_output(data, user.access_level if user else 0))

@app.route("/create-checkout-session/<tier>")
def create_checkout_session(tier):
    try:
        token = request.headers.get("X-User-Token")
        user = get_user_from_token(token)
        if not user:
            return {"status": "error", "msg": "non autenticato"}, 401
        if tier not in ["base", "full"]:
            return {"status": "error", "msg": "tier non valido"}, 400
        if not stripe:
            return {"status": "error", "msg": "Stripe non disponibile"}, 500
        price_id = STRIPE_PRICE_BASE if tier == "base" else STRIPE_PRICE_FULL
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=BASE_URL + "/success?token=" + user.token + "&tier=" + tier,
            cancel_url=BASE_URL + "/",
            metadata={"user_id": user.id, "tier": tier}
        )
        return {"status": "ok", "url": session.url}
    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500

@app.route("/success")
def success():
    token = request.args.get("token", "")
    tier = request.args.get("tier", "")
    if token and tier:
        user = get_user_from_token(token)
        if user:
            user.access_level = 1 if tier == "base" else 2
            db.session.commit()
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        event = stripe.Webhook.construct_event(request.data, request.headers.get("Stripe-Signature"), WEBHOOK_SECRET)
    except Exception as e:
        return {"error": str(e)}, 400
    if event["type"] == "checkout.session.completed":
        s = event["data"]["object"]
        user = db.session.get(User, int(s["metadata"]["user_id"]))
        if user:
            user.access_level = 1 if s["metadata"]["tier"] == "base" else 2
            db.session.commit()
    return {"status": "ok"}

@app.route("/admin/upgrade", methods=["POST"])
def admin_upgrade():
    data = request.get_json(silent=True) or {}
    if data.get("secret") != ADMIN_SECRET:
        return {"status": "error", "msg": "unauthorized"}, 401
    user = User.query.filter_by(email=data.get("email","")).first()
    if not user:
        return {"status": "error", "msg": "user not found"}, 404
    user.access_level = int(data.get("level", 1))
    db.session.commit()
    return {"status": "ok", "email": user.email, "access_level": user.access_level}

@app.route("/healthz")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
