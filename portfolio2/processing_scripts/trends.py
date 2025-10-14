import pandas as pd
import time
from pytrends.request import TrendReq

# === CONFIGURACIÓN ===
cryptos_populares = [
    "Bitcoin",
    "Ethereum",
    "Tether",
    "BNB",
    "Solana"
]

# Lista de países (agrega los que necesites)
countries = ['US','MX', 'BR', 'CN', 'JP', 'DE', 'GB', 'IN', 'KR', 'SG']

# Nombre del CSV acumulativo
output_csv = "crypto_trends.csv"

# === CARGA O CREACIÓN DEL DATAFRAME ===
try:
    all_trends_df = pd.read_csv(output_csv)
    print("📂 Archivo existente encontrado. Se cargarán los datos previos.")
except FileNotFoundError:
    all_trends_df = pd.DataFrame()
    print("🆕 No existe archivo previo. Se creará uno nuevo.")

# === PROCESAMIENTO POR PAÍS ===
for country in countries:
    # Saltar si el país ya está en el CSV
    if not all_trends_df.empty and country in all_trends_df["country"].unique():
        print(f"⏭️ País {country} ya procesado, se salta.")
        continue

    print(f"🌎 Descargando datos para {country}...")

    # Conectar con Google Trends
    pytrends = TrendReq(hl="en-US", tz=360, timeout=5)

    try:
        pytrends.build_payload(
            kw_list=cryptos_populares,
            timeframe="today 5-y",
            geo=country
        )
        df = pytrends.interest_over_time().reset_index()
    except Exception as e:
        print(f"⚠️ Error al obtener datos de {country}: {e}")
        continue

    if df.empty:
        print(f"⚠️ No se obtuvieron datos para {country}, se salta.")
        continue

    # Agregar columna de país
    df["country"] = country

    # Reestructurar formato long
    df_melt = df.melt(
        id_vars=["date", "country"],
        value_vars=cryptos_populares,
        var_name="keyword",
        value_name="interest"
    )

    # Concatenar
    all_trends_df = pd.concat([all_trends_df, df_melt], ignore_index=True)

    # Guardar CSV acumulativo
    all_trends_df.to_csv(output_csv, index=False)
    print(f"✅ Datos de {country} añadidos y guardados.\n")

    # Espera de 30 segundos para evitar rate limit
    print("⏳ Esperando 30 segundos antes del siguiente país...\n")
    time.sleep(30)

print("🎉 Proceso completado. Archivo final guardado en:", output_csv)
