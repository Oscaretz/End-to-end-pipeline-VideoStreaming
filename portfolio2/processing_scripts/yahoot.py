# ============================================
# CRYPTOCURRENCY PRICES (Yahoo Finance)
# ============================================

import yfinance as yf
import pandas as pd
import time

# Criptomonedas a descargar (Yahoo Finance tickers)
cryptos_populares = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Tether": "USDT-USD",
    "BNB": "BNB-USD",
    "Solana": "SOL-USD"
}

print("="*60)
print("DESCARGA DE DATOS DE CRIPTOMONEDAS - Yahoo Finance")
print("="*60)

# Lista para almacenar DataFrames individuales
all_data = []

# Descargar datos para cada criptomoneda INDIVIDUALMENTE
for crypto_name, ticker_symbol in cryptos_populares.items():
    print(f"\n📈 Descargando {crypto_name} ({ticker_symbol})...")
    
    try:
        # Crear objeto Ticker
        ticker = yf.Ticker(ticker_symbol)
        
        # Obtener histórico usando el método history()
        data = ticker.history(period="5y", interval="1d", auto_adjust=True)
        
        # Verificar si se descargaron datos
        if data.empty:
            print(f"  ⚠️  No se encontraron datos para {crypto_name}")
            continue
        
        # Resetear el índice para convertir Date en columna
        data = data.reset_index()
        
        # Renombrar columna Date si es necesario
        if 'Date' not in data.columns and 'index' in data.columns:
            data = data.rename(columns={'index': 'Date'})
        
        # Agregar columna con el nombre de la criptomoneda
        data['crypto'] = crypto_name
        
        # Seleccionar y ordenar solo las columnas que necesitamos
        # Usar solo las columnas que existen
        available_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        cols_to_keep = [col for col in available_cols if col in data.columns]
        cols_to_keep.append('crypto')
        
        data = data[cols_to_keep]
        
        # Reordenar para que crypto esté después de Date
        data = data[['Date', 'crypto', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Agregar a la lista
        all_data.append(data)
        
        print(f"  ✓ {crypto_name}: {len(data):,} registros descargados")
        print(f"    Rango: {data['Date'].min()} a {data['Date'].max()}")
        print(f"    Columnas: {list(data.columns)}")
        
        # Pequeña pausa entre descargas
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ✗ Error al descargar {crypto_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        continue

# Verificar si se descargaron datos
if not all_data:
    print("\n❌ No se pudieron descargar datos de ninguna criptomoneda")
    exit(1)

# Combinar todos los DataFrames
print(f"\n{'='*60}")
print("CONSOLIDANDO DATOS...")
print(f"{'='*60}")

crypto_prices = pd.concat(all_data, ignore_index=True)

# Verificar tipo de columnas
print(f"Tipo de columnas: {type(crypto_prices.columns)}")
print(f"Columnas: {list(crypto_prices.columns)}")

# Formatear la fecha
crypto_prices['Date'] = pd.to_datetime(crypto_prices['Date']).dt.strftime('%Y-%m-%d')

# Ordenar por fecha y criptomoneda
crypto_prices = crypto_prices.sort_values(['Date', 'crypto']).reset_index(drop=True)

# Guardar en CSV
output_file = "crypto_prices_yahoo.csv"
crypto_prices.to_csv(output_file, index=False)