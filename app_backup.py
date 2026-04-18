from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import subprocess, json, os, re, time
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "super-secret-key-change-in-prod")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

CORS(app, supports_credentials=True)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400 * 30
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_DOMAIN"] = None
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
app.config["REMEMBER_COOKIE_DURATION"] = 86400 * 30
db = SQLAlchemy(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
login_manager = LoginManager(app)

def get_user_from_token(token):
    if not token:
        return None
    import hashlib
    for u in User.query.all():
        expected = hashlib.sha256(f"{u.id}-{u.email}-diagn-eco-2026".encode()).hexdigest()
        if expected == token:
            return u
    return None



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    access_level = db.Column(db.Integer, default=0)
    created_at = db.Column(db.Float, default=time.time)

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    stripe_session_id = db.Column(db.String(200))
    amount = db.Column(db.Integer)
    tier = db.Column(db.String(20))
    status = db.Column(db.String(20))
    created_at = db.Column(db.Float, default=time.time)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def clean_value(s):
    s = s.strip().strip('"').strip("'").strip()
    s = re.sub(r"[€\s]", "", s)
    s = s.replace(" ", "")
    parts = s.split(".")
    if len(parts) > 1 and len(parts[-1]) != 2:
        s = "".join(parts)
    s = s.replace(",", ".")
    return s

def normalize_csv(file_path):
    rows = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line = line.replace(";", ",")
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                continue
            date, client = parts[0].strip(), parts[1].strip()
            if not date or not client:
                continue
            # Formato impiantisti: client, revenue, hours, cost_hour, materials, estimate
            if len(parts) >= 6:
                try:
                    revenue = float(clean_value(parts[2]))
                    hours = float(clean_value(parts[3]))
                    cost_hour = float(clean_value(parts[4]))
                    materials = float(clean_value(parts[5]))
                    estimate = float(clean_value(parts[6])) if len(parts) > 6 else 0
                    rows.append([date, client, revenue, hours, cost_hour, materials, estimate])
                    continue
                except:
                    pass
            # Formato base: date, client, value
            value = clean_value(parts[2])
            try:
                float(value)
                rows.append([date, client, float(value), 0, 0, 0, 0])
            except:
                continue
    if not rows:
        raise Exception("CSV vuoto o formato non valido")
    df = pd.DataFrame(rows, columns=["date","client","revenue","hours","cost_hour","materials","estimate"])
    df.to_csv("normalized.csv", index=False, header=False)
    return "normalized.csv"

def filter_output(data, access_level):
    if access_level == 0:
        return {
            "access_level": 0,
            "loss_90d": data.get("loss_90d", 0),
            "recovery_potential": data.get("recovery_potential", 0),
            "diagnosis": data.get("diagnosis", ""),
            "locked": True
        }
    elif access_level == 1:
        return {
            "access_level": 1,
            "loss_90d": data.get("loss_90d", 0),
            "recovery_potential": data.get("recovery_potential", 0),
            "diagnosis": data.get("diagnosis", ""),
            "action": data.get("action", ""),
            "worst_client": data.get("worst_client", ""),
            "worst_margin": data.get("worst_margin", 0),
            "best_client": data.get("best_client", ""),
            "best_margin": data.get("best_margin", 0),
            "total_margin": data.get("total_margin", 0),
            "top_losses": data.get("top_losses", []),
            "loss_annual": data.get("loss_annual", 0),
            "locked": False
        }
    else:
        data["access_level"] = 2
        data["locked"] = False
        return data

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/auth", methods=["POST"])
def auth():
    try:
        data = request.json
        email = data.get("email", "").strip().lower()
        if not email or "@" not in email:
            return {"status": "error", "msg": "email non valida"}, 400
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, access_level=0)
            db.session.add(user)
            db.session.commit()
        login_user(user, remember=True, duration=__import__('datetime').timedelta(days=30))
        # Genera token semplice per produzione
        import hashlib
        token = hashlib.sha256(f"{user.id}-{user.email}-diagn-eco-2026".encode()).hexdigest()
        return {"status": "ok", "user_id": user.id, "access_level": user.access_level, "email": user.email, "token": token}
    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500

@app.route("/me")
def me():
    if current_user.is_authenticated:
        return {"status": "ok", "user_id": current_user.id, "access_level": current_user.access_level, "email": current_user.email}
    return {"status": "anonymous", "access_level": 0}

@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def analyze():
    try:
        if "file" not in request.files:
            return {"status": "error", "msg": "no file"}, 400
        f = request.files["file"]
        f.save("data.csv")
        if os.path.getsize("data.csv") > 2 * 1024 * 1024:
            os.remove("data.csv")
            return {"status": "error", "msg": "file troppo grande (max 2MB)"}, 413
        normalized_path = normalize_csv("data.csv")
        result = subprocess.run(["./cashflow" if __import__("os").path.exists("./cashflow") else "/opt/render/project/src/cashflow", normalized_path, "1000"], capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return {"status": "error", "msg": "engine failed", "stderr": result.stderr}, 500
        full_data = json.loads(result.stdout)
        # Prova prima con token header (per produzione), poi con sessione
        token = request.headers.get('X-User-Token')
        token_user = get_user_from_token(token)
        if token_user:
            access_level = token_user.access_level
        elif current_user.is_authenticated:
            access_level = current_user.access_level
        else:
            access_level = 0
        return jsonify(filter_output(full_data, access_level))
    except subprocess.TimeoutExpired:
        return {"status": "error", "msg": "analisi troppo lunga"}, 504
    except Exception as e:
        return {"status": "error", "msg": str(e)}, 500

@app.route("/admin/upgrade", methods=["POST"])
def admin_upgrade():
    secret = request.json.get("secret", "")
    if secret != os.environ.get("ADMIN_SECRET", "admin-secret-local"):
        return {"status": "error", "msg": "unauthorized"}, 401
    email = request.json.get("email", "")
    level = int(request.json.get("level", 1))
    user = User.query.filter_by(email=email).first()
    if not user:
        return {"status": "error", "msg": "user not found"}, 404
    user.access_level = level
    db.session.commit()
    return {"status": "ok", "email": email, "access_level": level}

@app.route("/healthz")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout():
    data = request.get_json()
    tier = data.get("tier")

    token = request.headers.get('X-User-Token')
    user = get_user_from_token(token)

    if not user:
        return {"status": "error", "msg": "non autenticato"}, 401

    if tier not in ["base", "full"]:
        return {"status": "error", "msg": "tier non valido"}, 400

    import stripe as stripe_lib
    import os

    stripe_lib.api_key = os.environ.get("STRIPE_SECRET_KEY")

    price_id = (
        "price_XXXXXXXX_BASE" if tier == "base"
        else "price_XXXXXXXX_FULL"
    )

    checkout = stripe_lib.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        success_url="https://diagn-eco.onrender.com/success",
        cancel_url="https://diagn-eco.onrender.com/",
        metadata={"user_id": user.id, "tier": tier}
    )

    return {"status": "ok", "url": checkout.url}

