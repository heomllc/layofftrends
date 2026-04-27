#!/usr/bin/env python3
"""
LayoffTrends API — Flask + SQLite
Runs on port 5000, proxied via Nginx at /api/
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, jwt, hashlib, secrets, json, os, time
from datetime import datetime, timezone, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app, origins=["https://layofftrends.com", "http://localhost"])

# ── CONFIG ───────────────────────────────────────────────────────────────────
DB_PATH  = "/var/www/layofftrends.com/data/layofftrends.db"
JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID", "")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ── DATABASE ─────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE,
            name        TEXT,
            avatar      TEXT,
            provider    TEXT,          -- 'google' | 'twitter' | 'email'
            provider_id TEXT,
            password_hash TEXT,
            created_at  TEXT DEFAULT (datetime('now')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS experiences (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER REFERENCES users(id),
            company      TEXT NOT NULL,
            sector       TEXT,
            verdict      TEXT NOT NULL,   -- 'bad' | 'ok' | 'good'
            score_notice      INTEGER DEFAULT 3,
            score_severance   INTEGER DEFAULT 3,
            score_comms       INTEGER DEFAULT 3,
            score_outplacement INTEGER DEFAULT 3,
            score_humanity    INTEGER DEFAULT 3,
            story        TEXT,
            job_title    TEXT,
            location     TEXT,
            linkedin     TEXT,
            helpful_count INTEGER DEFAULT 0,
            is_seed      INTEGER DEFAULT 0,
            created_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS helpful_votes (
            user_id       INTEGER,
            experience_id INTEGER,
            PRIMARY KEY (user_id, experience_id)
        );

        CREATE INDEX IF NOT EXISTS idx_exp_company ON experiences(company);
        CREATE INDEX IF NOT EXISTS idx_exp_verdict  ON experiences(verdict);
        CREATE INDEX IF NOT EXISTS idx_exp_created  ON experiences(created_at);
    """)
    conn.commit()
    conn.close()

# ── SEED DATA ─────────────────────────────────────────────────────────────────
SEED_EXPERIENCES = [
    ("Tesla",      "Technology", "bad",  1,2,1,1,1, "Woke up to find my badge wasn't working. No call, no email — just a Slack message at 6am. Two weeks severance after 4 years. Leadership posted a blog about 'exciting transformation' the same day.", "Senior Software Engineer", "Fremont, CA"),
    ("Stripe",     "Technology", "good", 5,5,5,4,5, "Stripe gave 14 weeks severance plus COBRA fully paid for 6 months. Patrick Collison sent a personal email. Managers called each of us individually. It still hurt but they treated us like humans.", "Product Manager", "San Francisco, CA"),
    ("Intel",      "Technology", "bad",  2,3,2,2,2, "60 days WARN notice but they put us in limbo where we couldn't work on anything meaningful. Communication from leadership was all corporate speak. No genuine acknowledgment of what was happening to 15,000 people.", "Principal Engineer", "Santa Clara, CA"),
    ("Shopify",    "Technology", "good", 4,5,4,5,5, "16 weeks severance, extended health benefits for a full year, and they set up an internal talent marketplace. CEO Tobi made a personal video. Clearly thought hard about making it as humane as possible.", "Engineering Manager", "Ottawa, Canada"),
    ("Cisco",      "Technology", "ok",   3,3,2,3,3, "Severance was OK — 3 weeks per year of service. Communication was corporate and rehearsed. No personal touch from leadership. The actual people managers were kind but had no information to share.", "Solutions Architect", "Research Triangle, NC"),
    ("Meta",       "Technology", "bad",  1,3,2,2,2, "System access cut at midnight. Found out from a friend who texted me a news article. HR reached out hours later. The way it was executed — automated, overnight — felt deliberately dehumanizing.", "Data Scientist", "Menlo Park, CA"),
    ("HubSpot",    "Technology", "good", 4,4,5,4,5, "HubSpot handled this better than any layoff I've heard of. 12 weeks severance, fully paid health for 3 months, accelerated vesting, and the CEO posted a public list of all affected employees on LinkedIn to help them get hired.", "Account Executive", "Boston, MA"),
    ("Citigroup",  "Finance",    "bad",  2,2,1,2,1, "Escorted out by security on the same day as the announcement. Three weeks severance for 6 years of service. My manager didn't even know it was happening until that morning.", "Operations Analyst", "New York, NY"),
    ("Spotify",    "Media",      "ok",   3,4,3,3,3, "Decent severance — 5 months plus equity. But the communication from Daniel Ek felt disconnected from reality. Very uneven experience depending on your team.", "Product Designer", "Stockholm, Sweden"),
    ("Amazon",     "Technology", "bad",  2,2,2,1,2, "Amazon's WARN period felt like surveillance — they stopped assigning work and monitored activity. Outplacement was a portal with links to job boards. Dehumanizing at scale.", "Software Engineer II", "Seattle, WA"),
    ("Salesforce", "Technology", "ok",   3,3,3,2,3, "Decent package but the communication was cold. Got an email before the manager call. Felt like a number. Outplacement was offered but generic.", "Senior AE", "San Francisco, CA"),
    ("Twitter/X",  "Technology", "bad",  1,2,1,1,1, "Fired via email. No severance negotiation, just a take-it-or-leave-it. Access cut before the email was even read by some people. No outplacement. Elon tweeted about it while we were processing.", "Engineering Manager", "San Francisco, CA"),
]

def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM experiences WHERE is_seed=1").fetchone()[0]
    if count == 0:
        for row in SEED_EXPERIENCES:
            company, sector, verdict, n, s, c, o, h, story, title, location = row
            conn.execute("""
                INSERT INTO experiences
                (company, sector, verdict, score_notice, score_severance, score_comms,
                 score_outplacement, score_humanity, story, job_title, location, is_seed)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,1)
            """, (company, sector, verdict, n, s, c, o, h, story, title, location))
        conn.commit()
        print(f"Seeded {len(SEED_EXPERIENCES)} experiences")
    conn.close()

# ── AUTH HELPERS ──────────────────────────────────────────────────────────────
def make_token(user_id, email, name):
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def upsert_user(email, name, avatar, provider, provider_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=?", (email,)
    ).fetchone()
    if user:
        conn.execute(
            "UPDATE users SET name=?, avatar=?, last_login=datetime('now') WHERE id=?",
            (name, avatar, user["id"])
        )
        conn.commit()
        user_id = user["id"]
    else:
        cur = conn.execute(
            "INSERT INTO users (email, name, avatar, provider, provider_id) VALUES (?,?,?,?,?)",
            (email, name, avatar, provider, provider_id)
        )
        conn.commit()
        user_id = cur.lastrowid
    conn.close()
    return user_id

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────

@app.route("/api/auth/google", methods=["POST"])
def auth_google():
    """Verify Google ID token and return our JWT"""
    data = request.json or {}
    id_token = data.get("id_token")
    if not id_token:
        return jsonify({"error": "Missing id_token"}), 400
    try:
        # Verify with Google
        import urllib.request as ur
        resp = ur.urlopen(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}",
            timeout=8
        )
        info = json.loads(resp.read().decode())
        if info.get("aud") != GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID:
            return jsonify({"error": "Invalid audience"}), 401
        email  = info.get("email", "")
        name   = info.get("name", email.split("@")[0])
        avatar = info.get("picture", "")
        user_id = upsert_user(email, name, avatar, "google", info.get("sub"))
        token = make_token(user_id, email, name)
        return jsonify({"token": token, "user": {"id": user_id, "name": name, "email": email, "avatar": avatar}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/auth/email/register", methods=["POST"])
def email_register():
    data = request.json or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name     = (data.get("name") or email.split("@")[0]).strip()
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Email already registered. Please sign in."}), 409
    cur = conn.execute(
        "INSERT INTO users (email, name, provider, password_hash) VALUES (?,?,?,?)",
        (email, name, "email", hash_password(password))
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    token = make_token(user_id, email, name)
    return jsonify({"token": token, "user": {"id": user_id, "name": name, "email": email}})

@app.route("/api/auth/email/login", methods=["POST"])
def email_login():
    data = request.json or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=? AND provider='email'", (email,)).fetchone()
    conn.close()
    if not user or user["password_hash"] != hash_password(password):
        return jsonify({"error": "Incorrect email or password"}), 401
    conn = get_db()
    conn.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
    conn.commit()
    conn.close()
    token = make_token(user["id"], email, user["name"])
    return jsonify({"token": token, "user": {"id": user["id"], "name": user["name"], "email": email}})

@app.route("/api/auth/me", methods=["GET"])
@require_auth
def auth_me():
    return jsonify({"user": request.user})

# ── EXPERIENCE ROUTES ─────────────────────────────────────────────────────────

def row_to_dict(row):
    d = dict(row)
    avg = (d["score_notice"] + d["score_severance"] + d["score_comms"] +
           d["score_outplacement"] + d["score_humanity"]) / 5
    d["avg_score"] = round(avg, 1)
    d["scores"] = {
        "notice":       d.pop("score_notice"),
        "severance":    d.pop("score_severance"),
        "comms":        d.pop("score_comms"),
        "outplacement": d.pop("score_outplacement"),
        "humanity":     d.pop("score_humanity"),
    }
    # Relative time
    try:
        dt = datetime.fromisoformat(d["created_at"])
        diff = datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)
        if diff.days >= 1:
            d["time"] = f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            d["time"] = f"{diff.seconds//3600}h ago"
        else:
            d["time"] = f"{diff.seconds//60}m ago"
    except:
        d["time"] = "Recently"
    return d

@app.route("/api/experiences", methods=["GET"])
def get_experiences():
    verdict = request.args.get("verdict")
    company = request.args.get("company")
    limit   = min(int(request.args.get("limit", 50)), 200)
    offset  = int(request.args.get("offset", 0))

    conn = get_db()
    where, params = ["1=1"], []
    if verdict:
        where.append("verdict=?"); params.append(verdict)
    if company:
        where.append("LOWER(company)=LOWER(?)"); params.append(company)

    rows = conn.execute(f"""
        SELECT e.*, u.name as user_name, u.avatar as user_avatar
        FROM experiences e
        LEFT JOIN users u ON e.user_id = u.id
        WHERE {' AND '.join(where)}
        ORDER BY e.created_at DESC
        LIMIT ? OFFSET ?
    """, params + [limit, offset]).fetchall()
    conn.close()
    return jsonify({"experiences": [row_to_dict(r) for r in rows]})

@app.route("/api/experiences/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    total   = conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
    bad     = conn.execute("SELECT COUNT(*) FROM experiences WHERE verdict='bad'").fetchone()[0]
    good    = conn.execute("SELECT COUNT(*) FROM experiences WHERE verdict='good'").fetchone()[0]
    companies = conn.execute("SELECT COUNT(DISTINCT company) FROM experiences").fetchone()[0]
    users   = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    # Company scores
    rows = conn.execute("""
        SELECT company,
               COUNT(*) as count,
               AVG((score_notice+score_severance+score_comms+score_outplacement+score_humanity)/5.0) as avg,
               SUM(CASE WHEN verdict='bad'  THEN 1 ELSE 0 END) as bad_count,
               SUM(CASE WHEN verdict='good' THEN 1 ELSE 0 END) as good_count,
               SUM(CASE WHEN verdict='ok'   THEN 1 ELSE 0 END) as ok_count
        FROM experiences
        GROUP BY LOWER(company)
        ORDER BY avg ASC
    """).fetchall()
    conn.close()

    company_scores = [dict(r) for r in rows]
    shame = sorted(company_scores, key=lambda x: x["avg"])[:6]
    fame  = sorted(company_scores, key=lambda x: x["avg"], reverse=True)[:6]

    return jsonify({
        "total":     total,
        "bad":       bad,
        "good":      good,
        "ok":        total - bad - good,
        "pct_bad":   round(bad/total*100) if total else 0,
        "pct_good":  round(good/total*100) if total else 0,
        "companies": companies,
        "users":     users,
        "shame":     shame,
        "fame":      fame,
    })

@app.route("/api/experiences", methods=["POST"])
@require_auth
def post_experience():
    data = request.json or {}
    company = (data.get("company") or "").strip()
    verdict = data.get("verdict")
    if not company or verdict not in ("bad", "ok", "good"):
        return jsonify({"error": "Company and verdict are required"}), 400

    scores = data.get("scores") or {}
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO experiences
        (user_id, company, sector, verdict,
         score_notice, score_severance, score_comms, score_outplacement, score_humanity,
         story, job_title, location, linkedin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        request.user["sub"],
        company,
        data.get("sector", ""),
        verdict,
        scores.get("notice", 3),
        scores.get("severance", 3),
        scores.get("comms", 3),
        scores.get("outplacement", 3),
        scores.get("humanity", 3),
        data.get("story", ""),
        data.get("title", ""),
        data.get("location", ""),
        data.get("linkedin", ""),
    ))
    conn.commit()
    exp_id = cur.lastrowid
    conn.close()
    return jsonify({"id": exp_id, "message": "Experience submitted successfully"}), 201

@app.route("/api/experiences/<int:exp_id>/helpful", methods=["POST"])
@require_auth
def mark_helpful(exp_id):
    user_id = request.user["sub"]
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO helpful_votes (user_id, experience_id) VALUES (?,?)",
            (user_id, exp_id)
        )
        conn.execute(
            "UPDATE experiences SET helpful_count = helpful_count + 1 WHERE id=?",
            (exp_id,)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Already voted"}), 409

# ── ADMIN ─────────────────────────────────────────────────────────────────────
@app.route("/api/admin/stats", methods=["GET"])
@require_auth
def admin_stats():
    conn = get_db()
    users_by_provider = conn.execute("""
        SELECT provider, COUNT(*) as count FROM users GROUP BY provider
    """).fetchall()
    recent_users = conn.execute("""
        SELECT name, email, provider, created_at FROM users
        ORDER BY created_at DESC LIMIT 20
    """).fetchall()
    conn.close()
    return jsonify({
        "by_provider": [dict(r) for r in users_by_provider],
        "recent_users": [dict(r) for r in recent_users],
    })

# ── HEALTH ────────────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "time": datetime.now(timezone.utc).isoformat()})

# ── STARTUP ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    seed_db()
    print("LayoffTrends API starting on port 5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
