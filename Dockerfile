FROM apache/airflow:2.8.4

# Instala dependencias del sistema y driver ODBC para SQL Server
USER root
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libpq-dev \
    curl \
    gnupg2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Microsoft ODBC Driver para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Python requirements
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt