# Data Warehouse creator script for MsSQLServer.

from scripts.db.mssqlClient import connect_to_mssql
from scripts.sqlScriptExecutor import execute_sql_ddl_script
from config import get_mssql_config

from pathlib import Path

def get_base_dir():
    return Path(__file__).resolve().parent.parent

def generate_layer_schemas(server, database, username, password):
    # Change these values according to your MsSQLServer setup.
    server = server or "localhost"    # Or the Docker container name if using Docker.
    database = database or "your_database"
    username = username or "sa"
    password = password or "your_secure_password"

    # Paths to the SQL scripts.
    BASE_DIR = get_base_dir()
    root_script_path = BASE_DIR / "sql" / "DDL" / "schemasCreationQuery.sql"

    connection = connect_to_mssql(server, database, username, password)

    if connection:
        execute_sql_ddl_script(connection, root_script_path)
        connection.close()
        print("MsSQLServer connection closed.")
    else:
        print("Failed to connect to MsSQLServer.")
    
def main():
    # Get the configuration from the config module.
    mssql_cfg = get_mssql_config()

    # Generate the Data Warehouse schema.
    generate_layer_schemas(**mssql_cfg)

if __name__ == "__main__":
    main()