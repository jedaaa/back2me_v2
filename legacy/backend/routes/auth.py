"""
Authentication routes: /register  /login  /logout  /me
"""

import os, re, hashlib, datetime
from flask import Blueprint, request, jsonify, make_response
from config.database import get_db
import jwt
from bson import ObjectId

auth_bp  = Blueprint("auth", __name__)
SECRET   = os.environ.get("JWT_SECRET", "back2me_super_secret_2024")
ALGO     = "HS256"
EXP_DAYS = 7


def _hash_pw(plain: str) -> str:
    """SHA-256 hash (no extra deps). For production use bcrypt."""
    return hashlib.sha256(plain.encode()).hexdigest()


def _make_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=EXP_DAYS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def verify_token(token: str):
    """Return user_id string or None."""
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        return payload["sub"]
    except Exception as e:
        if os.environ.get("FLASK_ENV") != "production":
            print(f"  ✗ Token verification failed: {e}", flush=True)
        return None


def _set_token_cookie(response, token: str):
    if os.environ.get("FLASK_ENV") != "production":
        print(f"  → Setting token cookie (len={len(token)})", flush=True)
    response.set_cookie(
        "token", token,
        httponly=True, 
        samesite="Lax",
        path="/",
        max_age=60 * 60 * 24 * EXP_DAYS,
        secure=False # Ensure it's False for local HTTP
    )
    return response


# ─── helpers ──────────────────────────────────────────────

def _ser(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


def _email_valid(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e))


# ─── routes ───────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    if os.environ.get("FLASK_ENV") != "production":
        print(f"\n[Auth] Registration attempt for {request.get_json(silent=True).get('email')}", flush=True)

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be ≥ 3 characters"}), 400
    if not _email_valid(email):
        return jsonify({"error": "Invalid email address"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be ≥ 6 characters"}), 400

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409
    if db.users.find_one({"username": {"$regex": f"^{re.escape(username)}$", "$options": "i"}}):
        return jsonify({"error": "Username taken"}), 409

    user = {
        "username":        username,
        "email":           email,
        "hashed_password": _hash_pw(password),
        "profile_image":   f"https://ui-avatars.com/api/?name={username}&background=6366f1&color=fff&size=128",
        "created_at":      datetime.datetime.utcnow(),
    }
    result = db.users.insert_one(user)
    token  = _make_token(str(result.inserted_id))
    resp   = make_response(jsonify({"message": "Registered successfully", "username": username}), 201)
    return _set_token_cookie(resp, token)


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db   = get_db()
    user = db.users.find_one({"email": email})
    if not user or user["hashed_password"] != _hash_pw(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = _make_token(str(user["_id"]))
    resp  = make_response(jsonify({
        "message":  "Login successful",
        "username": user["username"],
        "user_id":  str(user["_id"]),
    }), 200)
    return _set_token_cookie(resp, token)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"message": "Logged out"}), 200)
    resp.delete_cookie("token", path="/")
    return resp


@auth_bp.route("/me", methods=["GET"])
def me():
    token   = request.cookies.get("token")
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    db   = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id":       str(user["_id"]),
        "username":      user["username"],
        "email":         user["email"],
        "profile_image": user.get("profile_image", ""),
    })


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"error": "Email required"}), 400

    db   = get_db()
    user = db.users.find_one({"email": email})
    # Always return success to avoid user enumeration
    return jsonify({"message": "If that email is registered, a reset link has been sent."})
