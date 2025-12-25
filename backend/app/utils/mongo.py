def serialize_mongo(doc: dict | None):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def serialize_mongo_list(docs: list):
    return [serialize_mongo(doc) for doc in docs]
