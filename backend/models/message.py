"""
Message Model - Rebuild v2.1
Handles private communication between users.
"""
import datetime
from bson.objectid import ObjectId
from .base import BaseModel

class Message(BaseModel):
    collection_name = "messages"

    @classmethod
    def send(cls, sender_id, receiver_id, text):
        msg_data = {
            "sender_id": ObjectId(sender_id),
            "receiver_id": ObjectId(receiver_id),
            "message_text": text.strip(),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "read": False
        }
        cls.get_collection().insert_one(msg_data)
        return True

    @classmethod
    def get_thread(cls, user_a, user_b):
        ua, ub = ObjectId(user_a), ObjectId(user_b)
        query = {
            "$or": [
                {"sender_id": ua, "receiver_id": ub},
                {"sender_id": ub, "receiver_id": ua}
            ]
        }
        cursor = cls.get_collection().find(query).sort("created_at", 1)
        return cls.serialize(list(cursor))

    @classmethod
    def get_conversations(cls, user_id):
        uid = ObjectId(user_id)
        pipeline = [
            {"$match": {"$or": [{"sender_id": uid}, {"receiver_id": uid}]}},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": {
                    "$cond": [
                        {"$eq": ["$sender_id", uid]}, 
                        "$receiver_id", 
                        "$sender_id"
                    ]
                },
                "last_message": {"$first": "$message_text"},
                "last_time": {"$first": "$created_at"},
                "unread": {"$sum": {"$cond": [{"$and": [{"$eq": ["$receiver_id", uid]}, {"$eq": ["$read", False]}]}, 1, 0]}}
            }}
        ]
        results = list(cls.get_collection().aggregate(pipeline))
        return cls.serialize(results)
