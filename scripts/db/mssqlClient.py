import pyodbc

def connect_to_mssql(server, database, username, password, driver="{ODBC Driver 17 for SQL Server}"):
    try:
        conn = pyodbc.connect(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        )
        print("Successful connection to SQL Server.")
        return conn
    except Exception as e:
        print("Error connecting to MsSQLServer:", e)
        return None