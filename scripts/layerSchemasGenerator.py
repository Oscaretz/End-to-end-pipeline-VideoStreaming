# Data Warehouse creator script for MsSQLServer.

from scripts.db.mssqlClient import connect_to_mssql
from config import get_mssql_config
from pathlib import Path

def get_base_dir():
    return Path(__file__).resolve().parent.parent

def generate_layer_schemas(server, database, username, password):
    # Change these values according to your MsSQLServer setup.
    server = "mssql-db,1433"   # Cambiar a nombre del servicio en Docker
    database = "dbo"
    username = "SA"
    password = "Password_airflow10"

    print("Creating database and schemas step by step...")
    
    # PASO 1: Conectar a master y crear la base de datos
    print("Step 1: Creating database...")
    master_connection = connect_to_mssql(server, "master", username, password)
    
    if master_connection:
        try:
            cursor = master_connection.cursor()
            # Habilitar autocommit para CREATE DATABASE
            master_connection.autocommit = True
            
            # Crear la base de datos
            cursor.execute(f"""
                IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{database}')
                BEGIN
                    CREATE DATABASE [{database}];
                    PRINT 'Database {database} created successfully.';
                END
                ELSE
                    PRINT 'Database {database} already exists.';
            """)
            
            cursor.close()
            master_connection.close()
            print(f"Database '{database}' is ready.")
            
        except Exception as e:
            print(f"Error creating database: {e}")
            master_connection.close()
            return
    else:
        print("Failed to connect to master database.")
        return

    # PASO 2: Conectar a la nueva base de datos y crear esquemas
    print("Step 2: Creating schemas...")
    target_connection = connect_to_mssql(server, database, username, password)
    
    if target_connection:
        try:
            cursor = target_connection.cursor()
            
            # Crear esquemas uno por uno
            schemas = ['bronze', 'silver', 'gold']
            
            for schema in schemas:
                cursor.execute(f"""
                    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}')
                    BEGIN
                        EXEC('CREATE SCHEMA {schema}');
                        PRINT 'Schema {schema} created successfully.';
                    END
                    ELSE
                        PRINT 'Schema {schema} already exists.';
                """)
                target_connection.commit()
                print(f"Schema '{schema}' processed.")
            
            cursor.close()
            target_connection.close()
            print("All schemas created successfully. Database setup completed.")
            
        except Exception as e:
            print(f"Error creating schemas: {e}")
            target_connection.close()
    else:
        print(f"Failed to connect to target database '{database}'.")
    
def main():
    # Get the configuration from the config module.
    mssql_cfg = get_mssql_config()

    # Generate the Data Warehouse schema.
    generate_layer_schemas(**mssql_cfg)

if __name__ == "__main__":
    main()