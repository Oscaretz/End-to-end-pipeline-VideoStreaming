import pandas as pd
import mysql.connector

# Leer CSVs
users_df = pd.read_csv("C:/Users/DELL/pedrozoproject/users.csv")
sessions_df = pd.read_csv("C:/Users/DELL/pedrozoproject/viewing_sessions.csv")

# Convertir fechas
users_df['registration_date'] = pd.to_datetime(users_df['registration_date']).dt.date
sessions_df['watch_date'] = pd.to_datetime(sessions_df['watch_date']).dt.date

# Conexión a MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password="rootpass",
    database="mydb"
)
cursor = conn.cursor()

# Crear tabla users
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(10) PRIMARY KEY,
    age INT,
    country VARCHAR(50),
    subscription_type VARCHAR(20),
    registration_date DATE,
    total_watch_time_hours FLOAT
)
""")

# Crear tabla viewing_sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS viewing_sessions (
    session_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10),
    content_id VARCHAR(10),
    watch_date DATE,
    watch_duration_minutes INT,
    completion_percentage FLOAT,
    device_type VARCHAR(20),
    quality_level VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
""")

# Insertar datos en users
for i, row in users_df.iterrows():
    cursor.execute("""
    INSERT INTO users (user_id, age, country, subscription_type, registration_date, total_watch_time_hours)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, tuple(row))

# Insertar datos en viewing_sessions
for i, row in sessions_df.iterrows():
    cursor.execute("""
    INSERT INTO viewing_sessions (session_id, user_id, content_id, watch_date, watch_duration_minutes, completion_percentage, device_type, quality_level)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

# Guardar cambios
conn.commit()

# Cerrar conexión
cursor.close()
conn.close()

print("Datos insertados correctamente.")
