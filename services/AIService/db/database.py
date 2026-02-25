from typing import List, Dict, Any, Union
from pymongo.collection import Collection
from db.config import get_database
from datetime import datetime
import uuid

db = get_database()
collection = db["AIPosts"]

def addToDB(
    documents: List[Dict[str, Any]],
    ngo_id: str,
    campaign_id: str = "",
    ordered: bool = False
) -> Dict[str, Union[bool, List[Any], str]]:
    """
    Enrich posts with required metadata and save to DB.
    """
    try:
        enriched_docs = []

        for doc in documents:
            enriched_doc = {
                "postId": str(uuid.uuid4()),
                "caption": doc.get("caption", ""),
                "post_link": doc.get("post_link", ""),
                "music_link": doc.get("music_link", ""),
                "schedule_time": doc.get("schedule_time", ""),
                "createdAt": datetime.utcnow(),
                "associatedWith": ngo_id,
                "status": "pending_approval",
                "campaignId": campaign_id,
                "type": "image",
                "tags": doc.get("tags", []) 
            }

            enriched_docs.append(enriched_doc)

        result = collection.insert_many(enriched_docs, ordered=ordered)

        return {
            "success": True,
            "inserted_ids": result.inserted_ids
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": "UnknownError",
            "details": str(e)
        }
