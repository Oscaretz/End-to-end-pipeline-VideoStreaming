# Data ingestor script for multiple databases.
from scripts.db.mongoClient import connect_to_mongo
from scripts.db.mssqlClient import connect_to_mssql
from scripts.externalDataReader import read_json_file, read_csv_file
from config import get_mongo_config, get_mssql_config
from pathlib import Path

def get_base_dir():
    return Path(__file__).resolve().parent.parent

def ingest_json_to_mongo(database: str, port: str, filename: str):
    # Change these values according to your MongoDB setup.
    database = database or "database"
    port = port or "27017"
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
    server = server or "mssql-db"    # Nombre del servicio en Docker
    database = database or "mssql_db"
    username = username or "sa"
    password = password or "your_secure_password"
    
    connection = connect_to_mssql(server, database, username, password)
    df = read_csv_file(filename)
    
    if connection:
        cursor = connection.cursor()
        table_name = Path(filename).stem
        
        # Crear tabla en el esquema bronze (asumiendo que ya existe)
        full_table_name = f"bronze.{table_name}"
        cols = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in df.columns])
        
        # Create table dynamically based on DataFrame columns
        cursor.execute(f"IF OBJECT_ID('{full_table_name}', 'U') IS NULL CREATE TABLE {full_table_name} ({cols});")
        
        # Insert data row by row
        placeholders = ", ".join(["?"] * len(df.columns))
        insert_query = f"INSERT INTO {full_table_name} VALUES ({placeholders})"
        for row in df.itertuples(index=False, name=None):
            cursor.execute(insert_query, row)
        connection.commit()
        print(f"Inserted data from {filename} into SQL Server table '{full_table_name}' in database '{database}'.")
        cursor.close()
        connection.close()
        print("MsSQLServer connection closed.")
    else:
        print("Failed to connect to MsSQLServer.")

def main():
    # Get the configuration from the config module.
    mssql_cfg = get_mssql_config()
    mongo_cfg = get_mongo_config()

if __name__ == "__main__":
    main()