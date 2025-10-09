import os

import certifi
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


def create_pymongo_client(collection_name):
    uri = os.getenv("DB_CONNECTION")
    return PymongoClient(uri, collection_name)


class PymongoClient:
    def __init__(self, uri, collection_name, db_name="appDb"):
        self.client = MongoClient(
            uri, server_api=ServerApi("1"), tlsCAFile=certifi.where()
        )
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    # def __del__(self):
    #     self.client.close()

    def insert_one(self, document):
        return self.collection.insert_one(document).inserted_id

    def find_one(self, query):
        result = self.collection.find_one(query)
        self.clean_id(result)
        return result

    def find_many(self, query={}):
        return list(self.collection.find(query))

    def update_one(self, query, update):
        return self.collection.update_one(query, update)

    def delete_one(self, query):
        return self.collection.delete_one(query)

    def delete_many(self, query={}):
        return self.collection.delete_many(query)

    def clean_id(self, doc):
        if doc:
            doc["_id"] = str(doc["_id"])
