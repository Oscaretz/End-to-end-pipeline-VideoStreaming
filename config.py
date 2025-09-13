from dotenv import load_dotenv
import os

load_dotenv()  # load environment variables from .env file.

def get_mssql_config():
    return {
        "server": os.getenv("MSSQL_SERVER"),
        "database": os.getenv("MSSQL_DATABASE"),
        "username": os.getenv("MSSQL_USER"),
        "password": os.getenv("MSSQL_PASSWORD")
    }

def get_mongo_config():
    return {
        "database": os.getenv("MONGO_DATABASE"),
        "port": os.getenv("MONGO_PORT")
    }