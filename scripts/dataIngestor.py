# Data ingestor script for multiple databases.

from scripts.db.mongoClient import connect_to_mongo
from scripts.db.mssqlClient import connect_to_mssql

from scripts.dataGenerator import generate_all_data

from scripts.scriptExecutor import execute_sql_dml_script

from config import get_mssql_config, get_mysql_config, get_oracle_config, get_postgresql_config, get_sqlite_config

from pathlib import Path

def get_base_dir():
    return Path(__file__).resolve().parent.parent

def data_ingestor_mssql(server, database, username, password, N):
    # Change these values according to your MsSQLServer setup.
    server = server or "localhost"    # Or the Docker container name if using Docker.
    database = database or "your_database"
    username = username or "sa"
    password = password or "your_secure_password"

    # Paths to the SQL scripts.
    # BASE_DIR = get_base_dir()
    # root_script_path = BASE_DIR / "sql" / "DML" / "MsSQLServer" / "rootTablesInsertionQuery.sql"
    # middle_script_path = BASE_DIR / "sql" / "DML" / "MsSQLServer" / "middleTablesInsertionQuery.sql"
    # last_script_path = BASE_DIR / "sql" / "DML" / "MsSQLServer" / "lastTablesInsertionQuery.sql"

    conn = connect_to_mssql(server, database, username, password)
    
    if conn:
        data = generate_all_data(N)
        print("Inserting data into MsSQLServer...")
        # execute_sql_dml_script(conn, root_script_path, data, N)
        # execute_sql_dml_script(conn, middle_script_path, data, N)
        # execute_sql_dml_script(conn, last_script_path, data, N)
        print("Data inserted successfully into MsSQLServer.")
        conn.close()

def main():
    # Load configurations.
    mssql_config = get_mssql_config()

    # Number of records to generate.
    N = 50

    # Example usage:
    data_ingestor_mssql(**mssql_config, N=N)

if __name__ == "__main__":
    main()