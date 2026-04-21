from bson import ObjectId


def normalize_doc(doc: dict | None) -> dict | None:
    if not doc:
        return None
    clean = dict(doc)
    if "_id" in clean and isinstance(clean["_id"], ObjectId):
        clean["_id"] = str(clean["_id"])
    return clean
