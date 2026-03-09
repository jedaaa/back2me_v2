import os
import sys
import logging
from flask import Flask, send_from_directory, request
from flask_cors import CORS

# Ensure backend directory is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db_connection
from utils.responses import api_success, api_error
from routes.auth import token_required

def create_app():
    app = Flask(__name__)
    
    # ── Configuration ──────────────────────────────────────────
    app.secret_key = os.environ.get("SECRET_KEY", "b2m_premium_secret_k_2024")
    PRODUCTION     = os.environ.get("FLASK_ENV") == "production"
    app.url_map.strict_slashes = False

    # ── Logging ───────────────────────────────────────────────
    log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server.log"))
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        force=True
    )

    @app.before_request
    def debug_log():
        if not PRODUCTION:
            rule = request.url_rule.rule if request.url_rule else "No match"
            print(f"[RECV] {request.method} {request.path} | {rule}", flush=True)

    # ── Security & CORS ───────────────────────────────────────
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5000", 
        "http://127.0.0.1:5000"
    ])

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    # ── Database Check ────────────────────────────────────────
    with app.app_context():
        try:
            conn = get_db_connection()
            if conn:
                print("MySQL Database Connected")
                conn.close()
            else:
                print("MySQL Database Failed to Connect")
        except Exception as e:
            logging.error(f"DB Startup Error: {e}")

    # ── Blueprints ────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.posts import posts_bp
    
    app.register_blueprint(auth_bp,     url_prefix="/api")
    app.register_blueprint(posts_bp,    url_prefix="/api/posts")

    # ── Upload Endpoint ───────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "uploads")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    import werkzeug.utils

    @app.route("/api/upload", methods=["POST", "OPTIONS"])
    def upload_image():
        if request.method == "OPTIONS":
            return api_success(message="Preflight ok")
        
        if "image" not in request.files:
            return api_error("No image file provided", "BAD_REQUEST", 400)
            
        file = request.files["image"]
        if file.filename == "":
            return api_error("No selected file", "BAD_REQUEST", 400)
            
        if file:
            filename = werkzeug.utils.secure_filename(file.filename)
            # Create a unique filename to prevent overwrites
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(file_path)
            
            # Return frontend accessible path
            file_url = f"/assets/uploads/{unique_filename}"
            return api_success(data={"image_url": file_url}, message="Image uploaded")

    # ── Health ────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "online", "version": "v3.0 (MySQL)"}

    # ── SPA / Static Routing ───────────────────────────────
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
        clean_path = path.replace('\\', '/')
        
        print(f"[DEBUG SPA] path={path}, clean_path={clean_path}, frontend_dir={frontend_dir}", flush=True)

        # Protect API namespace
        if clean_path.startswith("api/"):
            return api_error(f"Endpoint not found: {clean_path}", "NOT_FOUND", 404)

        # Serve static file if exists
        file_path = os.path.join(frontend_dir, *clean_path.split('/'))
        if clean_path and os.path.isfile(file_path):
            print(f"[DEBUG SPA] Serving static file: {file_path}", flush=True)
            return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path))
            
        # Fallback to index.html
        index_path = os.path.join(frontend_dir, "index.html")
        print(f"[DEBUG SPA] Fallback to index.html. Exists: {os.path.isfile(index_path)}", flush=True)
        return send_from_directory(frontend_dir, "index.html")

    # ── Global Errors ─────────────────────────────────────────
    @app.errorhandler(404)
    def handle_404(e):
        return api_error("Resource not found", "NOT_FOUND", 404)

    @app.errorhandler(405)
    def handle_405(e):
        return api_error(f"Method {request.method} not allowed", "METHOD_NOT_ALLOWED", 405)

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        logging.error(f"Unhandled Exception: {str(e)}\n{traceback.format_exc()}")
        return api_error("An internal error occurred", "INTERNAL_ERROR", 500)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
