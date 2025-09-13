from pymongo import MongoClient

def connect_to_mongo():
    try:
        conn = MongoClient("mongodb://mongodb:27017/")
        print("Successful connection to MongoDB.")
        return conn
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
