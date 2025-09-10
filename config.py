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

def get_mysql_config():
    return {
        "host": os.getenv("MYSQL_HOST"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE")
    }

def get_oracle_config():
    return {
        "username": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASSWORD"),
        "host": os.getenv("ORACLE_HOST")
    }

def get_postgresql_config():
    return {
        "host": os.getenv("POSTGRES_HOST"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "database": os.getenv("POSTGRES_DATABASE")
    }

def get_sqlite_config():
    return {
        "database": os.getenv("SQLITE_DATABASE")
    }

def get_data_warehouse_config():
    return {
        "server": os.getenv("MSSQL_DW_SERVER"),
        "database": os.getenv("MSSQL_DW_DATABASE"),
        "username": os.getenv("MSSQL_DW_USER"),
        "password": os.getenv("MSSQL_DW_PASSWORD")
    }