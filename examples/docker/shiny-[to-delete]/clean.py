import os


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


if __name__ == "__main__":
    URI = os.environ.get("MONGODB_CONNECTION_URI", "")

    client = MongoClient(URI, server_api=ServerApi("1"))

    try:
        client.admin.command("ping")
        print("Successfully connected to MongoDB!")
    except Exception as e:
        raise ConnectionError(str(e)) from e
    else:
        db = client.myDatabase
        my_collection = db["accuracy_scores"]

        my_collection.delete_many({})
        print("Collection cleared!")
