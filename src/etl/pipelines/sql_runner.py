import pyodbc

def run_sql_file(filename, **conn_config):
    with open(filename, "r") as f:
        sql_script = f.read()

    print("=== DEBUG CONNECTION CONFIG ===")
    print(conn_config)
    print("=== END DEBUG ===")

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={conn_config['server']},{conn_config.get('port', 1433)};"
        f"DATABASE={conn_config['database']};"
        f"UID={conn_config['username']};"
        f"PWD={conn_config['password']};"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=60;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(sql_script)
    conn.commit()
    cursor.close()
    conn.close()
