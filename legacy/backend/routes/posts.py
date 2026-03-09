"""
Post routes:
  POST   /posts           create post
  GET    /posts           all posts (paginated)
  GET    /posts/lost      only lost
  GET    /posts/found     only found
  GET    /posts/search    search (q, post_type)
  DELETE /posts/<id>      owner only
"""

import datetime, re
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from config.database import get_db
from routes.auth import verify_token

posts_bp = Blueprint("posts", __name__)
PAGE_SIZE = 20


# ─── helpers ──────────────────────────────────────────────

def _require_auth():
    """Return (user_id_str, None) or (None, error_response)."""
    token   = request.cookies.get("token")
    user_id = verify_token(token)
    if not user_id:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return user_id, None


def _format_post(post: dict) -> dict:
    post["_id"]     = str(post["_id"])
    post["user_id"] = str(post["user_id"])
    if "created_at" in post:
        post["created_at"] = post["created_at"].isoformat()
    return post


def _paginate(collection, query: dict, page: int):
    skip  = (page - 1) * PAGE_SIZE
    docs  = list(collection.find(query)
                            .sort("created_at", -1)
                            .skip(skip)
                            .limit(PAGE_SIZE))
    total = collection.count_documents(query)
    return [_format_post(d) for d in docs], total


# ─── routes ───────────────────────────────────────────────

@posts_bp.route("/posts", methods=["POST"])
def create_post():
    user_id, err = _require_auth()
    if err:
        return err

    data      = request.get_json(silent=True) or {}
    post_type = (data.get("post_type") or "").strip().lower()
    item_name = (data.get("item_name") or "").strip()
    place     = (data.get("place")     or "").strip()
    time_str  = (data.get("time")      or "").strip()
    location  = (data.get("location")  or "").strip()
    desc      = (data.get("description") or "").strip()
    image_url = (data.get("image_url") or "").strip()

    if post_type not in ("lost", "found"):
        return jsonify({"error": "post_type must be 'lost' or 'found'"}), 400
    if not item_name:
        return jsonify({"error": "item_name is required"}), 400
    if not location:
        return jsonify({"error": "location is required"}), 400
    if len(desc) > 200:
        return jsonify({"error": "description max 200 characters"}), 400

    db      = get_db()
    user    = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    doc = {
        "user_id":       ObjectId(user_id),
        "username":      user["username"],
        "profile_image": user.get("profile_image", ""),
        "post_type":     post_type,
        "item_name":     item_name,
        "place":         place,
        "time":          time_str,
        "location":      location,
        "description":   desc,
        "image_url":     image_url,
        "created_at":    datetime.datetime.utcnow(),
    }
    result = db.posts.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify({"message": "Post created", "post": _format_post(doc)}), 201


@posts_bp.route("/posts", methods=["GET"])
def get_all_posts():
    page = max(1, int(request.args.get("page", 1)))
    db   = get_db()
    docs, total = _paginate(db.posts, {}, page)
    return jsonify({"posts": docs, "total": total, "page": page, "page_size": PAGE_SIZE})


@posts_bp.route("/posts/lost", methods=["GET"])
def get_lost():
    page = max(1, int(request.args.get("page", 1)))
    db   = get_db()
    docs, total = _paginate(db.posts, {"post_type": "lost"}, page)
    return jsonify({"posts": docs, "total": total, "page": page})


@posts_bp.route("/posts/found", methods=["GET"])
def get_found():
    page = max(1, int(request.args.get("page", 1)))
    db   = get_db()
    docs, total = _paginate(db.posts, {"post_type": "found"}, page)
    return jsonify({"posts": docs, "total": total, "page": page})


@posts_bp.route("/posts/search", methods=["GET"])
def search_posts():
    q         = (request.args.get("q")         or "").strip()
    post_type = (request.args.get("post_type") or "all").strip().lower()
    page      = max(1, int(request.args.get("page", 1)))

    query: dict = {}

    if q:
        pattern = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [
            {"item_name":   pattern},
            {"place":       pattern},
            {"location":    pattern},
            {"description": pattern},
        ]

    if post_type in ("lost", "found"):
        query["post_type"] = post_type

    db   = get_db()
    docs, total = _paginate(db.posts, query, page)
    return jsonify({"posts": docs, "total": total, "page": page, "query": q})


@posts_bp.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    user_id, err = _require_auth()
    if err:
        return err
    try:
        oid = ObjectId(post_id)
    except InvalidId:
        return jsonify({"error": "Invalid post id"}), 400

    db     = get_db()
    result = db.posts.delete_one({"_id": oid, "user_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Not found or not authorized"}), 404
    return jsonify({"message": "Post deleted"})
