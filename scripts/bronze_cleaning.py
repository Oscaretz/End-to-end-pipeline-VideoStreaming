import pandas as pd
from scripts.db.mssqlClient import connect_to_mssql
from sqlalchemy import create_engine


# --- Funciones de limpieza ---
def clean_amazon_sales(df):
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    return df

def clean_cloud_warehouse(df):
    df = df.iloc[1:]  # saltar fila de encabezado si existe
    df.columns = ['Index','Operation','Price_INR','Price_Numeric']
    df['Price_INR'] = pd.to_numeric(df['Price_INR'].replace('₹','',regex=True), errors='coerce')
    df['Price_Numeric'] = pd.to_numeric(df['Price_Numeric'], errors='coerce')
    df['Index'] = pd.to_numeric(df['Index'], errors='coerce').fillna(0).astype(int)
    return df

def clean_expense_iigf(df):
    df = df.iloc[1:]
    df.columns = ['Index','Date','Amount1','Expense_Type','Amount2']
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['Amount'] = pd.to_numeric(df['Amount2'], errors='coerce').fillna(0)
    df = df[['Date','Expense_Type','Amount']]
    return df

def clean_international_sales(df):
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['PCS'] = pd.to_numeric(df['PCS'], errors='coerce').fillna(0).astype(int)
    df['RATE'] = pd.to_numeric(df['RATE'], errors='coerce')
    df['GROSS_AMT'] = pd.to_numeric(df['GROSS_AMT'], errors='coerce')
    df.columns = df.columns.str.strip().str.replace(' ','_')
    return df

# Función de limpieza para March 2021
def clean_march2021_pl(df):
    numeric_cols = df.columns[5:]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.columns = df.columns.str.strip().str.replace(' ','_')
    return df

# Función de limpieza para May 2022
def clean_may2022_pl(df):
    numeric_cols = df.columns[5:]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df.columns = df.columns.str.strip().str.replace(' ','_')
    return df

def clean_sale_report(df):
    df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
    df.columns = df.columns.str.strip().str.replace(' ','_')
    return df

# --- Tipos para Silver ---
SILVER_TYPES = {
    "AmazonSaleReportRow": {"Date": "DATE", "Qty": "INT", "Amount": "FLOAT"},
    "CloudWarehouseRow": {"Index": "INT", "Price_INR": "FLOAT", "Price_Numeric": "FLOAT"},
    "ExpenseIIGFRow": {"Date": "DATE", "Amount": "FLOAT", "Expense_Type": "NVARCHAR(255)"},
    "InternationalSalesRow": {"DATE": "DATE", "PCS": "INT", "RATE": "FLOAT", "GROSS_AMT": "FLOAT"},
    "PLMarch2021Row": {},
    "May2022Row": {},
    "SaleReportRow": {"Stock": "INT"}
}

# --- Función para procesar y copiar a Silver ---

def process_table(table_name: str, cleaning_function, silver_table_name: str = None):

    # Conexión raw (si la necesitas para otras operaciones)
    conn = connect_to_mssql("mssql_db", "dbo", "SA", "Password_airflow10")
    cursor = conn.cursor()
    
    # 🔹 Create SQLAlchemy engine
    connection_str = (
        "mssql+pyodbc://sa:Password_airflow10@mssql_db/dbo"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )
    engine = create_engine(connection_str)
    
    # Leer datos de Bronze
    df = pd.read_sql_query(f"SELECT * FROM bronze.[{table_name}]", engine)

    # Limpiar datos
    df = cleaning_function(df)

    # Si no se especifica, usar el mismo nombre de tabla
    if silver_table_name is None:
        silver_table_name = table_name

    # Mapear tipos de datos si están definidos
    dtype = SILVER_TYPES.get(f"{silver_table_name}Row", None)

    # Escribir en Silver
    df.to_sql(
        silver_table_name,
        con=engine,
        schema="silver",
        if_exists="replace",   # o "append" según tu caso
        index=False,
        dtype=dtype
    )

    print(f"✔️ Tabla {silver_table_name} copiada a Silver con {len(df)} filas")
