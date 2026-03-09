"""
Post Model - Rebuild v2.1
Handles lost & found report data.
"""
import datetime
from bson.objectid import ObjectId
from .base import BaseModel

class Post(BaseModel):
    collection_name = "posts"

    @classmethod
    def create(cls, user_id, item_name, post_type, description="", location="", image_url=""):
        post_data = {
            "user_id": ObjectId(user_id),
            "item_name": item_name.strip(),
            "post_type": post_type, # 'lost' or 'found'
            "description": description.strip(),
            "location": location.strip(),
            "image_url": image_url.strip(),
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        result = cls.get_collection().insert_one(post_data)
        return str(result.inserted_id)

    @classmethod
    def get_feed(cls, page=1, limit=10, post_type=None, search_query=None):
        query = {}
        if post_type in ["lost", "found"]:
            query["post_type"] = post_type
        
        if search_query:
            query["$text"] = {"$search": search_query}

        skip = (page - 1) * limit
        cursor = cls.get_collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        total = cls.get_collection().count_documents(query)
        posts = cls.serialize(list(cursor))
        
        return posts, total

    @classmethod
    def get_by_user(cls, user_id):
        cursor = cls.get_collection().find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
        return cls.serialize(list(cursor))
