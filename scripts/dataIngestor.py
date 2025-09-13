# Data ingestor script for multiple databases.

from scripts.db.mongoClient import connect_to_mongo
from scripts.db.mssqlClient import connect_to_mssql
from config import get_mssql_config, get_mongo_config
from externalDataReader import read_json_file, read_csv_file

from pathlib import Path

def get_base_dir():
    return Path(__file__).resolve().parent.parent


def ingest_json_to_mongo(database: str, port: str, filename: str):
    # Change these values according to your MongoDB setup.
    database = database or "database"
    port = port or "27018"

    connection = connect_to_mongo(port)
    db = connection[database]

    data = read_json_file(filename)

    # If JSON is a dict → insert one doc, if list → insert many
    collection_name = Path(filename).stem
    collection = db[collection_name]

    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

    print(f"Inserted data from {filename} into MongoDB collection '{collection_name}' in database '{database}'.")

def ingest_csv_to_mssql(server: str, database: str, username: str, password: str, filename: str):
    # Change these values according to your MsSQLServer setup.
    server = server or "localhost"    # Or the Docker container name if using Docker.
    database = database or "your_database"
    username = username or "sa"
    password = password or "your_secure_password"

    connection = connect_to_mssql(server, database, username, password)

    df = read_csv_file(filename)

    if connection:
        cursor = connection.cursor()
        
        table_name = Path(filename).stem

        # Create table dynamically based on DataFrame columns
        cols = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in df.columns])
        cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NULL CREATE TABLE {table_name} ({cols});")

        # Insert data row by row
        placeholders = ", ".join(["?"] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        for row in df.itertuples(index=False, name=None):
            cursor.execute(insert_query, row)

        connection.commit()
        print(f"Inserted data from {filename} into SQL Server table '{table_name}' in database '{database}'.")
        cursor.close()
        connection.close()
        print("MsSQLServer connection closed.")
    else:
        print("Failed to connect to MsSQLServer.")

def main():
    # Get the configuration from the config module.
    mssql_cfg = get_mssql_config()
    mongo_cfg = get_mongo_config()

    # Example usage
    ingest_json_to_mongo(**mongo_cfg, filename="example.json")
    ingest_csv_to_mssql(**mssql_cfg, filename="example.csv")

if __name__ == "__main__":
    main()
