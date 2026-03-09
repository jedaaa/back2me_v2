"""
Back2Me – Flask backend entry point
Run:  python app.py
Requires: pip install flask pymongo PyJWT flask-cors
"""

import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# ── import blueprints ──────────────────────────────────────
from routes.auth     import auth_bp
from routes.posts    import posts_bp
from routes.messages import messages_bp

# ── app factory ───────────────────────────────────────────
app = Flask(__name__)

# CORS configuration
CORS(app, supports_credentials=True,
     origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://0.0.0.0:5000"])

app.secret_key = os.environ.get("SECRET_KEY", "back2me_dev_key_2024")

# Production mode check
PRODUCTION = os.environ.get("FLASK_ENV") == "production"

# Performance optimization: Add cache headers
@app.after_request
def add_headers(response):
    """Add performance and security headers and log response cookies"""
    if not PRODUCTION:
        for cookie in response.headers.getlist('Set-Cookie'):
            print(f"  ← Set-Cookie: {cookie}", flush=True)
        print(f"  ← Status: {response.status_code}", flush=True)

    # Cache static files
    if request.path.startswith('/css/') or request.path.startswith('/js/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

# ── logging (only in debug mode) ─────────────────────────
if not PRODUCTION:
    @app.before_request
    def log_request():
        print(f"\n→ {request.method} {request.path}", flush=True)
        print(f"  Headers: {dict(request.headers)}", flush=True)
        if "token" in request.cookies:
            print(f"  Cookie Found: token={request.cookies['token'][:10]}...", flush=True)
        else:
            print("  No 'token' cookie found in request", flush=True)

# ── register blueprints (all under /api) ──────────────────
app.register_blueprint(auth_bp,     url_prefix="/api")
app.register_blueprint(posts_bp,    url_prefix="/api")
app.register_blueprint(messages_bp, url_prefix="/api")

# ── API routes ────────────────────────────────────────────
@app.route("/api/health")
def health():
    """Health check endpoint"""
    try:
        from config.database import get_db
        get_db()
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 503

# ── serve SPA (MUST BE LAST) ──────────────────────────────
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def serve_spa(path):
    """Serve frontend files or index.html for SPA routing - OPTIMIZED"""
    # CRITICAL: If path starts with api/, do NOT serve it as a static file
    # This prevents route shadowing and ensures 404/405 are handled by blueprints
    if path.startswith('api/') or path.startswith('/api/'):
        return jsonify({"error": "API route not found"}), 404

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
    
    # Try to serve the requested file
    if path:
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return send_from_directory(frontend_dir, path)
    
    # Default to index.html for SPA routing
    return send_from_directory(frontend_dir, "index.html")

# ── error handlers ────────────────────────────────────────
@app.errorhandler(405)
def method_not_allowed(e):
    print(f"  ✗ Method Not Allowed (405): {request.method} {request.path}", flush=True)
    return jsonify({
        "error": "Method Not Allowed",
        "method": request.method,
        "path": request.path
    }), 405
@app.errorhandler(500)
def server_error(e):
    print(f"  ✗ Server error: {e}", flush=True)
    return jsonify({"error": "Server error", "detail": str(e)}), 500

# ── run ───────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    
    print()
    print("╔" + "═" * 50 + "╗")
    print("║" + "  Back2Me – Lost & Found Platform".ljust(50) + "║")
    print("║" + f"  http://localhost:{port}".ljust(50) + "║")
    print("║" + f"  MongoDB: {os.environ.get('MONGO_URI', 'localhost:27017')}".ljust(50) + "║")
    print("╚" + "═" * 50 + "╝")
    print()
    
    app.run(host="0.0.0.0", port=port, debug=debug)
