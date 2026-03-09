"""
User Model - Rebuild v2.1
Handles authentication and user data.
"""
import datetime
import bcrypt
from .base import BaseModel

class User(BaseModel):
    collection_name = "users"

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def check_password(password, hashed):
        if not hashed: return False
        return bcrypt.checkpw(password.encode("utf-8"), hashed)

    @classmethod
    def create(cls, username, email, password):
        user_data = {
            "username": username.strip(),
            "email": email.strip().lower(),
            "password": cls.hash_password(password),
            "created_at": datetime.datetime.utcnow()
        }
        result = cls.get_collection().insert_one(user_data)
        return str(result.inserted_id)

    @classmethod
    def find_by_email(cls, email):
        user = cls.get_collection().find_one({"email": email.strip().lower()})
        return cls.serialize(user)

    @classmethod
    def find_by_username(cls, username):
        user = cls.get_collection().find_one({"username": username.strip()})
        return cls.serialize(user)

    @classmethod
    def exists(cls, email=None, username=None):
        query = []
        if email: query.append({"email": email.strip().lower()})
        if username: query.append({"username": username.strip()})
        
        if not query: return False
        return cls.get_collection().find_one({"$or": query}) is not None
