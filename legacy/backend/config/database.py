"""
MongoDB connection configuration.
Requires: pip install pymongo bcrypt
MongoDB URI can be overridden via MONGO_URI environment variable.
"""

import os
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.environ.get("DB_NAME", "back2me")

_client = None
_db     = None


def get_db():
    global _client, _db
    if _db is not None:
        return _db
    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")          # raises if unreachable
    _db = _client[DB_NAME]
    _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    # users
    db.users.create_index("email",    unique=True)
    db.users.create_index("username", unique=True)

    # posts – text index enables $text search
    db.posts.create_index([
        ("item_name",   TEXT),
        ("place",       TEXT),
        ("location",    TEXT),
        ("description", TEXT),
    ], name="post_text_idx")
    db.posts.create_index("post_type")
    db.posts.create_index("created_at")

    # messages
    db.messages.create_index([("sender_id", ASCENDING),
                               ("receiver_id", ASCENDING)])
    db.messages.create_index("timestamp")
