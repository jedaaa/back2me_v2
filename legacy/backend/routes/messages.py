"""
Message routes:
  POST  /messages                send a message
  GET   /messages/conversations  list all unique conversations for current user
  GET   /messages/<other_user_id> get thread between current user and other user
"""

import datetime
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from config.database import get_db
from routes.auth import verify_token

messages_bp = Blueprint("messages", __name__)


def _require_auth():
    token   = request.cookies.get("token")
    user_id = verify_token(token)
    if not user_id:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return user_id, None


def _fmt(msg: dict) -> dict:
    msg["_id"]         = str(msg["_id"])
    msg["sender_id"]   = str(msg["sender_id"])
    msg["receiver_id"] = str(msg["receiver_id"])
    if "timestamp" in msg:
        msg["timestamp"] = msg["timestamp"].isoformat()
    return msg


@messages_bp.route("/messages", methods=["POST"])
def send_message():
    user_id, err = _require_auth()
    if err:
        return err

    data        = request.get_json(silent=True) or {}
    receiver_id = (data.get("receiver_id") or "").strip()
    text        = (data.get("message_text") or "").strip()

    if not receiver_id or not text:
        return jsonify({"error": "receiver_id and message_text required"}), 400
    if len(text) > 1000:
        return jsonify({"error": "Message too long (max 1000 chars)"}), 400

    try:
        recv_oid = ObjectId(receiver_id)
    except InvalidId:
        return jsonify({"error": "Invalid receiver_id"}), 400

    if receiver_id == user_id:
        return jsonify({"error": "Cannot message yourself"}), 400

    db   = get_db()
    recv = db.users.find_one({"_id": recv_oid})
    if not recv:
        return jsonify({"error": "Receiver not found"}), 404

    msg = {
        "sender_id":    ObjectId(user_id),
        "receiver_id":  recv_oid,
        "message_text": text,
        "timestamp":    datetime.datetime.utcnow(),
    }
    result = db.messages.insert_one(msg)
    msg["_id"] = result.inserted_id
    return jsonify({"message": "Sent", "data": _fmt(msg)}), 201


@messages_bp.route("/messages/conversations", methods=["GET"])
def conversations():
    user_id, err = _require_auth()
    if err:
        return err

    db   = get_db()
    oid  = ObjectId(user_id)

    # find all distinct partners
    sent     = db.messages.distinct("receiver_id", {"sender_id": oid})
    received = db.messages.distinct("sender_id",   {"receiver_id": oid})
    partners = list({str(p) for p in sent + received})

    result = []
    for pid in partners:
        try:
            poid = ObjectId(pid)
        except Exception:
            continue
        partner = db.users.find_one({"_id": poid}, {"hashed_password": 0})
        if not partner:
            continue
        # last message
        last = db.messages.find_one(
            {"$or": [
                {"sender_id": oid,  "receiver_id": poid},
                {"sender_id": poid, "receiver_id": oid},
            ]},
            sort=[("timestamp", -1)]
        )
        result.append({
            "partner_id":      str(partner["_id"]),
            "partner_username": partner["username"],
            "partner_image":   partner.get("profile_image", ""),
            "last_message":    last["message_text"] if last else "",
            "last_timestamp":  last["timestamp"].isoformat() if last else "",
        })

    # sort by latest message
    result.sort(key=lambda x: x["last_timestamp"], reverse=True)
    return jsonify({"conversations": result})


@messages_bp.route("/messages/<other_id>", methods=["GET"])
def thread(other_id):
    user_id, err = _require_auth()
    if err:
        return err

    try:
        other_oid = ObjectId(other_id)
        me_oid    = ObjectId(user_id)
    except InvalidId:
        return jsonify({"error": "Invalid user id"}), 400

    db   = get_db()
    msgs = list(db.messages.find(
        {"$or": [
            {"sender_id": me_oid,    "receiver_id": other_oid},
            {"sender_id": other_oid, "receiver_id": me_oid},
        ]},
        sort=[("timestamp", 1)]
    ))
    return jsonify({"messages": [_fmt(m) for m in msgs]})
