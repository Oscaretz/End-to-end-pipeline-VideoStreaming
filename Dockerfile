FROM apache/airflow:2.8.4

# Instala dependencias del sistema si es necesario
USER root
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Python requirements
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt