from pymongo import MongoClient

def connect_to_mongo(port):
    try:
        conn = MongoClient(f"mongodb://mongo-db:{port}")
        print("Successful connection to MongoDB.")
        return conn
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
