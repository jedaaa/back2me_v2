import os
import datetime
import bcrypt
import jwt
from flask import Blueprint, request
from config.database import execute_query
from utils.responses import api_success, api_error

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "b2m_premium_secret_k_2024")

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return api_error("Missing or invalid token", "UNAUTHORIZED", 401)
        
        token = token.split(" ")[1]
        decoded = decode_token(token)
        if not decoded:
            return api_error("Token is expired or invalid", "UNAUTHORIZED", 401)
            
        return f(decoded["user_id"], *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

@auth_bp.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")

    data = request.get_json()
    if not data:
        return api_error("Invalid payload", "BAD_REQUEST", 400)

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return api_error("Missing required fields", "VALIDATION_FAILED", 400)

    # Check if user exists
    existing = execute_query(
        "SELECT id FROM users WHERE email = %s OR username = %s LIMIT 1",
        (email, username), fetchone=True
    )
    if existing:
        return api_error("Username or email already in use", "CONFLICT", 409)

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    try:
        user_id = execute_query(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, hashed)
        )
        token = generate_token(user_id)
        return api_success(
            data={"token": token, "user": {"id": user_id, "username": username, "email": email}},
            message="Registration successful", status=201
        )
    except Exception as e:
        return api_error(f"Failed to create user: {e}", "SERVER_ERROR", 500)

@auth_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")

    data = request.get_json()
    if not data:
        return api_error("Invalid payload", "BAD_REQUEST", 400)

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return api_error("Missing credentials", "VALIDATION_FAILED", 400)

    user = execute_query("SELECT * FROM users WHERE email = %s LIMIT 1", (email,), fetchone=True)
    if not user:
        return api_error("Invalid credentials", "UNAUTHORIZED", 401)

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return api_error("Invalid credentials", "UNAUTHORIZED", 401)

    token = generate_token(user["id"])
    return api_success(
        data={"token": token, "user": {"id": user["id"], "username": user["username"], "email": user["email"]}},
        message="Login successful"
    )

@auth_bp.route("/me", methods=["GET", "OPTIONS"])
@token_required
def me(user_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")

    user = execute_query("SELECT id, username, email, created_at FROM users WHERE id = %s LIMIT 1", (user_id,), fetchone=True)
    if not user:
        return api_error("User not found", "NOT_FOUND", 404)

    return api_success(data={"user": user})

@auth_bp.route("/logout", methods=["POST", "OPTIONS"])
def logout():
    return api_success(message="Logged out successfully")
