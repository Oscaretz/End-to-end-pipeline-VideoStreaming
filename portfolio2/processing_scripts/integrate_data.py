"""
============================================
SCRIPT 4: INTEGRACIÓN DE DATOS
Prepara datasets finales para análisis
============================================
"""

import pandas as pd
import numpy as np

print("="*80)
print("INTEGRACIÓN DE DATOS PARA ANÁLISIS")
print("="*80)

# ============================================
# 1. MAPEO DE PAÍSES
# ============================================
print("\n[1/5] Creando mapeo de países...")

country_mapping = {
    'US': {'iso3': 'USA', 'name': 'United States', 'region': 'Americas'},
    'MX': {'iso3': 'MEX', 'name': 'Mexico', 'region': 'Americas'},
    'BR': {'iso3': 'BRA', 'name': 'Brazil', 'region': 'Americas'},
    'CN': {'iso3': 'CHN', 'name': 'China', 'region': 'Asia'},
    'JP': {'iso3': 'JPN', 'name': 'Japan', 'region': 'Asia'},
    'DE': {'iso3': 'DEU', 'name': 'Germany', 'region': 'Europe'},
    'GB': {'iso3': 'GBR', 'name': 'United Kingdom', 'region': 'Europe'},
    'IN': {'iso3': 'IND', 'name': 'India', 'region': 'Asia'},
    'KR': {'iso3': 'KOR', 'name': 'South Korea', 'region': 'Asia'},
    'SG': {'iso3': 'SGP', 'name': 'Singapore', 'region': 'Asia'}
}

country_df = pd.DataFrame.from_dict(country_mapping, orient='index')
country_df.index.name = 'country_code'
country_df = country_df.reset_index()
country_df.to_csv('country_mapping.csv', index=False)
print(f"   ✓ country_mapping.csv guardado")

# ============================================
# 2. CARGAR Y LIMPIAR DATOS
# ============================================
print("\n[2/5] Cargando datos...")

# Cargar trends
try:
    trends = pd.read_csv('crypto_trends.csv')
    print(f"   ✓ crypto_trends.csv: {len(trends):,} registros")
except FileNotFoundError:
    trends = pd.read_csv('google_trends_data.csv')
    print(f"   ✓ google_trends_data.csv: {len(trends):,} registros")

# Cargar precios
prices = pd.read_csv('crypto_prices_yahoo.csv')
print(f"   ✓ crypto_prices_yahoo.csv: {len(prices):,} registros")

# Cargar geo data
geo = pd.read_csv('geo_countries.csv')
print(f"   ✓ geo_countries.csv: {len(geo):,} registros")

# ============================================
# 3. ENRIQUECER TRENDS CON INFO GEOGRÁFICA
# ============================================
print("\n[3/5] Enriqueciendo Google Trends...")

# Convertir fechas
trends['date'] = pd.to_datetime(trends['date'])

# Merge con mapeo de países
trends_enriched = trends.merge(
    country_df, 
    left_on='country', 
    right_on='country_code', 
    how='left'
)

# Agregar coordenadas manualmente (más confiable)
coords_dict = {
    'United States': (-77.0369, 38.9072),
    'Mexico': (-99.1332, 19.4326),
    'Brazil': (-47.8825, -15.7975),
    'China': (116.4074, 39.9042),
    'Japan': (139.6917, 35.6895),
    'Germany': (13.4050, 52.5200),
    'United Kingdom': (-0.1278, 51.5074),
    'India': (77.2090, 28.6139),
    'South Korea': (126.9780, 37.5665),
    'Singapore': (103.8198, 1.3521)
}

# Crear columnas lon y lat
trends_enriched['lon'] = trends_enriched['name'].map(lambda x: coords_dict.get(x, (None, None))[0] if pd.notna(x) else None)
trends_enriched['lat'] = trends_enriched['name'].map(lambda x: coords_dict.get(x, (None, None))[1] if pd.notna(x) else None)

trends_enriched.to_csv('trends_enriched.csv', index=False)
print(f"   ✓ trends_enriched.csv: {len(trends_enriched):,} registros")
print(f"   ✓ Nuevas columnas: iso3, name, region, lon, lat")

# ============================================
# 4. CALCULAR MÉTRICAS DE VOLATILIDAD
# ============================================
print("\n[4/5] Calculando métricas de precios...")

prices['Date'] = pd.to_datetime(prices['Date'])
prices = prices.sort_values(['crypto', 'Date'])

# Retornos
prices['returns'] = prices.groupby('crypto')['Close'].pct_change()
prices['log_returns'] = np.log(prices['Close'] / prices.groupby('crypto')['Close'].shift(1))

# Volatilidad rolling
prices['volatility_7d'] = prices.groupby('crypto')['returns'].transform(
    lambda x: x.rolling(window=7, min_periods=1).std()
)
prices['volatility_30d'] = prices.groupby('crypto')['returns'].transform(
    lambda x: x.rolling(window=30, min_periods=1).std()
)

# Retornos al cuadrado (para GARCH/clustering)
prices['returns_squared'] = prices['returns'] ** 2

# Precio normalizado (para comparaciones)
prices['price_normalized'] = prices.groupby('crypto')['Close'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min())
)

prices.to_csv('prices_with_metrics.csv', index=False)
print(f"   ✓ prices_with_metrics.csv: {len(prices):,} registros")
print(f"   ✓ Nuevas columnas: returns, log_returns, volatility_7d, volatility_30d, returns_squared")

# ============================================
# 5. DATASET INTEGRADO (SPATIOTEMPORAL)
# ============================================
print("\n[5/5] Creando dataset integrado...")

# Renombrar columnas para hacer merge
trends_for_merge = trends_enriched.rename(columns={
    'date': 'Date',
    'keyword': 'crypto'  # Renombrar keyword a crypto
})

print(f"   Columnas en trends_for_merge: {list(trends_for_merge.columns)}")
print(f"   Columnas en prices: {list(prices.columns)}")

# Merge completo
integrated = trends_for_merge.merge(
    prices,
    on=['Date', 'crypto'],
    how='inner'
)

print(f"   Registros después del merge: {len(integrated):,}")

integrated.to_csv('integrated_data.csv', index=False)
print(f"   ✓ integrated_data.csv: {len(integrated):,} registros")

# ============================================
# 6. AGREGACIONES POR PAÍS
# ============================================
print("\n[6/5] BONUS: Agregaciones por país...")

country_agg = integrated.groupby(['country_code', 'name', 'crypto']).agg({
    'interest': ['mean', 'std', 'max'],
    'volatility_7d': ['mean', 'std'],
    'volatility_30d': ['mean', 'std'],
    'returns': ['mean', 'std'],
    'Close': ['mean', 'min', 'max']
}).reset_index()

# Aplanar columnas MultiIndex
country_agg.columns = ['_'.join(col).strip('_') for col in country_agg.columns.values]

country_agg.to_csv('country_aggregated.csv', index=False)
print(f"   ✓ country_aggregated.csv: {len(country_agg):,} registros")


print(f"\nDimensiones: {integrated.shape[0]:,} filas × {integrated.shape[1]} columnas")
print(f"Rango de fechas: {integrated['Date'].min()} a {integrated['Date'].max()}")
print(f"Países: {integrated['country_code'].nunique()}")
print(f"Criptomonedas: {integrated['crypto'].nunique()}")

print("\nColumnas disponibles:")
for i, col in enumerate(integrated.columns, 1):
    print(f"   {i:2d}. {col}")

print("\n" + "="*80)
print("MUESTRA DEL DATASET INTEGRADO")
print("="*80)

sample_cols = ['Date', 'country_code', 'name', 'crypto', 'interest', 
               'Close', 'volatility_7d', 'returns']
available_sample_cols = [col for col in sample_cols if col in integrated.columns]

print(integrated[available_sample_cols].head(15).to_string(index=False))

print("\n" + "="*80)
print("CORRELACIONES BÁSICAS")
print("="*80)

corr_cols = ['interest', 'Close', 'volatility_7d', 'volatility_30d', 'returns']
available_corr_cols = [col for col in corr_cols if col in integrated.columns]

if len(available_corr_cols) > 1:
    corr_matrix = integrated[available_corr_cols].corr()
    print("\n", corr_matrix.round(3))

print("\n✅ Todo listo para el análisis!")