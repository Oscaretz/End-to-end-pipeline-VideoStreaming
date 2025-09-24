import pandas as pd
from scripts.db.mssqlClient import connect_to_mssql
from config import get_mssql_config

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
    cfg = get_mssql_config()
    conn = connect_to_mssql(cfg["server"], cfg["database"], cfg["username"], cfg["password"])
    cursor = conn.cursor()
    
    # Leer datos de Bronze
    df = pd.read_sql_query(f"SELECT * FROM bronze.[{table_name}]", conn)
    
    # Limpiar datos
    df_clean = cleaning_function(df)
    
    # Nombre final en Silver
    silver_name = silver_table_name if silver_table_name else table_name
    
    # Crear tabla en Silver con tipos correctos
    types = SILVER_TYPES.get(silver_name, {})  # ahora usa silver_table_name para consistencia
    for col in df_clean.columns:
        if col not in types:
            if pd.api.types.is_integer_dtype(df_clean[col]):
                types[col] = 'INT'
            elif pd.api.types.is_float_dtype(df_clean[col]):
                types[col] = 'FLOAT'
            elif pd.api.types.is_datetime64_any_dtype(df_clean[col]):
                types[col] = 'DATE'
            else:
                types[col] = 'NVARCHAR(MAX)'

    columns_sql = ", ".join([f"[{col}] {types[col]}" for col in df_clean.columns])
    
    cursor.execute(f"""
        IF NOT EXISTS (SELECT * FROM sys.objects 
                       WHERE object_id = OBJECT_ID(N'silver.[{silver_name}]') 
                       AND type in (N'U'))
        BEGIN
            CREATE TABLE silver.[{silver_name}] ({columns_sql})
        END
    """)
    conn.commit()
    
    # Insertar datos
    for index, row in df_clean.iterrows():
        cols = ','.join([f"[{col}]" for col in row.index])
        vals_list = []
        for col, x in zip(row.index, row.values):
            col_type = types.get(col, 'NVARCHAR(MAX)')
            if pd.notnull(x):
                if col_type in ['INT', 'FLOAT', 'DECIMAL']:
                    vals_list.append(f"{x}")
                elif col_type == 'DATE':
                    vals_list.append(f"'{pd.to_datetime(x).strftime('%Y-%m-%d')}'")
                else:
                    val = str(x).replace("'", "''")
                    vals_list.append(f"'{val}'")
            else:
                vals_list.append('NULL')
        vals = ','.join(vals_list)
        cursor.execute(f"INSERT INTO silver.[{silver_name}] ({cols}) VALUES ({vals})")
    
    conn.commit()
    cursor.close()
    conn.close()
