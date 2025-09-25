from pathlib import Path
import pandas as pd
from scripts.db.mssqlClient import connect_to_mssql
from config import get_mssql_config

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_DIR = BASE_DIR / "data"  # Carpeta que contiene todos los CSVs

def safe_sql_name(name: str) -> str:
    """
    Escapa corchetes en nombres para SQL Server, 
    reemplaza espacios por guiones bajos, 
    y agrega corchetes alrededor.
    """
    name = name.replace(" ", "_")  # <<< Reemplaza espacios
    name = name.replace("]", "]]")
    return f"[{name}]"

def ingest_csv_to_mssql(server, database, username, password, csv_path):
    connection = connect_to_mssql(server, database, username, password)
    df = pd.read_csv(csv_path)
    cursor = connection.cursor()
    
    schema = "bronze"
    # Reemplazar espacios en el nombre de la tabla
    table_name = Path(csv_path).stem.replace(" ", "_")

    # Crear esquema bronze si no existe
    cursor.execute(f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema}') EXEC('CREATE SCHEMA {schema}');")
    
    full_table_name = f"{safe_sql_name(schema)}.{safe_sql_name(table_name)}"
    
    # Crear tabla si no existe
    cols = ", ".join([f"{safe_sql_name(col)} NVARCHAR(MAX)" for col in df.columns])
    cursor.execute(f"IF OBJECT_ID('{full_table_name}', 'U') IS NULL CREATE TABLE {full_table_name} ({cols});")
    
    # Insertar fila por fila (convertir a string y reemplazar NaN por None)
    placeholders = ", ".join(["?"] * len(df.columns))
    insert_query = f"INSERT INTO {full_table_name} VALUES ({placeholders})"
    
    for row in df.itertuples(index=False, name=None):
        row_safe = [str(x) if pd.notnull(x) else None for x in row]
        cursor.execute(insert_query, row_safe)
    
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Inserted data from {csv_path} into table {full_table_name}.")

def ingest_all_csvs():
    cfg = get_mssql_config()
    for csv_file in CSV_DIR.glob("*.csv"):
        print(f"Processing {csv_file}")
        ingest_csv_to_mssql(
            server="mssql_db,1433",
            database="dbo",
            username="SA",
            password="Password_airflow10",
            csv_path=csv_file
        )

if __name__ == "__main__":
    ingest_all_csvs()
