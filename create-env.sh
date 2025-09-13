#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the .env file path
ENV_FILE="$SCRIPT_DIR/.env"

# Create or overwrite the .env file.
# Change values for the ones that you want.
cat > "$ENV_FILE" <<EOL
# MSSQL Server
MSSQL_SERVER=localhost
MSSQL_DATABASE=mssql_db
MSSQL_USER=sa
MSSQL_PASSWORD=your_secure_password
MSSQL_PORT=1434

# MONGO DATABASE.
MONGO_PORT=27018
MONGO_DATABASE=mongo_db

# AIRFLOW AUTH CREDENTIALS.
AIRFLOW_USER=airflow
AIRFLOW_PASSWORD=airflow
EOL

echo ".env file created successfully at: $ENV_FILE"
