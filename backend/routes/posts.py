from flask import Blueprint, request
from config.database import execute_query
from utils.responses import api_success, api_error
from routes.auth import token_required

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("", methods=["POST", "OPTIONS"])
@token_required
def create_post(user_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")

    data = request.get_json()
    if not data:
        return api_error("Invalid payload", "BAD_REQUEST", 400)

    item_name = data.get("item_name", "").strip()
    post_type = data.get("post_type")
    description = data.get("description", "").strip()
    location = data.get("location", "").strip()
    image_url = data.get("image_url", "").strip()

    if not item_name or post_type not in ["lost", "found"]:
        return api_error("Item name and type ('lost' or 'found') are required", "VALIDATION_FAILED", 400)

    try:
        post_id = execute_query(
            """INSERT INTO posts (user_id, item_name, post_type, description, location, image_url)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, item_name, post_type, description, location, image_url)
        )
        return api_success(data={"post_id": post_id}, message="Post created successfully", status=201)
    except Exception as e:
        return api_error(f"Failed to create post: {str(e)}", "SERVER_ERROR", 500)

@posts_bp.route("", methods=["GET", "OPTIONS"])
def get_posts():
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")

    post_type = request.args.get("type")
    search_query = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    query = """
    SELECT p.*, u.username 
    FROM posts p 
    JOIN users u ON p.user_id = u.id 
    WHERE 1=1
    """
    params = []

    if post_type in ["lost", "found"]:
        query += " AND p.post_type = %s"
        params.append(post_type)
        
    if search_query:
        query += " AND p.item_name LIKE %s"
        params.append(f"%{search_query}%")

    # Count total
    count_query = query.replace("SELECT p.*, u.username", "SELECT COUNT(*) as total")
    total_result = execute_query(count_query, params, fetchone=True)
    total = total_result["total"] if total_result else 0

    query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        posts = execute_query(query, params, fetchall=True)
        return api_success(data={"posts": posts, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return api_error(f"Failed to fetch posts: {str(e)}", "SERVER_ERROR", 500)

@posts_bp.route("/user/<int:target_user_id>", methods=["GET", "OPTIONS"])
def get_user_posts(target_user_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")
        
    query = """
    SELECT p.*, u.username 
    FROM posts p 
    JOIN users u ON p.user_id = u.id 
    WHERE p.user_id = %s
    ORDER BY p.created_at DESC
    """
    posts = execute_query(query, (target_user_id,), fetchall=True)
    return api_success(data={"posts": posts})

@posts_bp.route("/<int:post_id>", methods=["DELETE", "OPTIONS"])
@token_required
def delete_post(user_id, post_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")
        
    post = execute_query("SELECT user_id FROM posts WHERE id = %s", (post_id,), fetchone=True)
    if not post:
        return api_error("Post not found", "NOT_FOUND", 404)
        
    if post["user_id"] != user_id:
        return api_error("Unauthorized to delete this post", "UNAUTHORIZED", 403)
        
    execute_query("DELETE FROM posts WHERE id = %s", (post_id,))
    return api_success(message="Post deleted successfully")

# --- COMMENTS & REPLIES ---

@posts_bp.route("/<int:post_id>/comments", methods=["GET", "OPTIONS"])
def get_comments(post_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")
        
    query = """
    SELECT c.*, u.username 
    FROM comments c
    JOIN users u ON c.user_id = u.id
    WHERE c.post_id = %s
    ORDER BY c.created_at ASC
    """
    try:
        comments = execute_query(query, (post_id,), fetchall=True)
        return api_success(data={"comments": comments})
    except Exception as e:
        return api_error(f"Failed to fetch comments: {str(e)}", "SERVER_ERROR", 500)

@posts_bp.route("/<int:post_id>/comments", methods=["POST", "OPTIONS"])
@token_required
def add_comment(user_id, post_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")
        
    data = request.get_json()
    if not data:
        return api_error("Invalid payload", "BAD_REQUEST", 400)
        
    text = data.get("comment_text", "").strip()
    if not text:
        return api_error("Comment text is required", "VALIDATION_FAILED", 400)
        
    # Check if post exists
    post = execute_query("SELECT id FROM posts WHERE id = %s", (post_id,), fetchone=True)
    if not post:
        return api_error("Post not found", "NOT_FOUND", 404)
        
    try:
        comment_id = execute_query(
            "INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)",
            (post_id, user_id, text)
        )
        return api_success(data={"comment_id": comment_id}, message="Comment added", status=201)
    except Exception as e:
        return api_error(f"Failed to add comment: {str(e)}", "SERVER_ERROR", 500)

# --- POST RESOLUTION ---

@posts_bp.route("/<int:post_id>/resolve", methods=["PUT", "OPTIONS"])
@token_required
def resolve_post(user_id, post_id):
    if request.method == "OPTIONS":
        return api_success(message="Preflight ok")
        
    post = execute_query("SELECT user_id, status FROM posts WHERE id = %s", (post_id,), fetchone=True)
    if not post:
        return api_error("Post not found", "NOT_FOUND", 404)
        
    if post["user_id"] != user_id:
        return api_error("Only the original author can resolve this post", "UNAUTHORIZED", 403)
        
    if post["status"] == "resolved":
        return api_error("Post is already marked as resolved.", "CONFLICT", 409)
        
    try:
        execute_query("UPDATE posts SET status = 'resolved' WHERE id = %s", (post_id,))
        return api_success(message="Post successfully marked as resolved")
    except Exception as e:
        return api_error(f"Failed to update post status: {str(e)}", "SERVER_ERROR", 500)

