"""
Base Model - Rebuild v2.1
Provides common DB access and serialization utilities.
"""
from bson.objectid import ObjectId
from config.database import get_db

class BaseModel:
    collection_name = None

    @classmethod
    def get_collection(cls):
        if not cls.collection_name:
            raise NotImplementedError("Collection name not defined.")
        return get_db()[cls.collection_name]

    @staticmethod
    def serialize(data):
        """Converts Mongo documents to JSON-safe dictionaries."""
        if data is None:
            return None
        
        if isinstance(data, list):
            return [BaseModel.serialize(item) for item in data]
        
        # Deep copy style conversion
        serialized = dict(data)
        if "_id" in serialized:
            serialized["_id"] = str(serialized["_id"])
        
        # Convert any other ObjectIds found in common fields
        for key in ["user_id", "sender_id", "receiver_id", "post_id"]:
            if key in serialized and isinstance(serialized[key], ObjectId):
                serialized[key] = str(serialized[key])
        
        return serialized

    @classmethod
    def find_by_id(cls, doc_id):
        try:
            doc = cls.get_collection().find_one({"_id": ObjectId(doc_id)})
            return cls.serialize(doc)
        except:
            return None

    @classmethod
    def delete_by_id(cls, doc_id):
        try:
            return cls.get_collection().delete_one({"_id": ObjectId(doc_id)}).deleted_count > 0
        except:
            return False
