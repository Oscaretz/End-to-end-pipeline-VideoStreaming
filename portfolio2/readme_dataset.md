# Cryptocurrency Analysis Dataset

This repository contains a comprehensive dataset for analyzing cryptocurrencies from both temporal and spatial perspectives, combining Google Trends search interest data with Yahoo Finance price data.

## 📊 Dataset Overview

**Period:** October 2020 - October 2025 (5 years)  
**Cryptocurrencies:** Bitcoin, Ethereum, Tether, BNB, Solana  
**Countries:** United States, Mexico, Brazil, China, Japan, Germany, United Kingdom, India, South Korea, Singapore  
**Total Records:** ~13,100 (trends) + ~9,130 (prices)

---

## 🗂️ Files Description

### 📁 Core Data Files

#### 1. `prices_with_metrics.csv`
**Source:** Yahoo Finance (via `yahoot.py`)  
**Frequency:** Daily  
**Records:** 9,130 rows (1,826 days × 5 cryptos)

Contains historical price data with calculated metrics for time series analysis.

**Columns:**
- `Date` - Trading date (YYYY-MM-DD)
- `crypto` - Cryptocurrency name
- `Open`, `High`, `Low`, `Close` - OHLC prices (USD)
- `Volume` - Trading volume
- `returns` - Daily returns (%)
- `log_returns` - Logarithmic returns
- `volatility_7d` - 7-day rolling volatility
- `volatility_30d` - 30-day rolling volatility
- `returns_squared` - Squared returns (for volatility clustering)
- `price_normalized` - Min-max normalized price (0-1)

**Use for:** Part 1 - Time Series Analysis (ACF, Random Walk, Volatility)

---

#### 2. `trends_enriched.csv`
**Source:** Google Trends (via `trends.py`) + Geographic enrichment  
**Frequency:** Weekly  
**Records:** 13,100 rows

Contains search interest data enriched with geographic information.

**Columns:**
- `date` - Week start date (YYYY-MM-DD)
- `country` - ISO-2 country code (US, MX, BR, etc.)
- `keyword` - Cryptocurrency name
- `interest` - Search interest (0-100, normalized by Google)
- `country_code` - ISO-2 code (duplicate for reference)
- `iso3` - ISO-3 country code (USA, MEX, BRA, etc.)
- `name` - Full country name
- `region` - Geographic region (Americas, Asia, Europe)
- `lon` - Longitude of country capital
- `lat` - Latitude of country capital

**Use for:** Part 2 - Spatial Analysis (Choropleth maps, Regional time series)

---

#### 3. `integrated_data.csv` ⭐
**Source:** Merged from trends + prices (via `integrate_data.py`)  
**Frequency:** Weekly (limited by Google Trends)  
**Records:** ~6,500 rows (merged on matching dates)

Complete integrated dataset combining search interest and price metrics.

**Columns:** All columns from both `trends_enriched.csv` and `prices_with_metrics.csv`

**Key Variables:**
- Geographic: `country`, `name`, `region`, `lon`, `lat`
- Search: `interest`
- Price: `Close`, `Volume`
- Volatility: `volatility_7d`, `volatility_30d`
- Returns: `returns`, `log_returns`, `returns_squared`

**Use for:** Part 3 - Spatiotemporal Integration (Cross-correlation, Lead-Lag analysis)

---

#### 4. `country_aggregated.csv`
**Source:** Aggregated from `integrated_data.csv`  
**Records:** 50 rows (10 countries × 5 cryptos)

Summary statistics by country and cryptocurrency.

**Columns:**
- `country_code`, `name`, `crypto`
- `interest_mean`, `interest_std`, `interest_max`
- `volatility_7d_mean`, `volatility_7d_std`
- `volatility_30d_mean`, `volatility_30d_std`
- `returns_mean`, `returns_std`
- `Close_mean`, `Close_min`, `Close_max`

**Use for:** Part 3 - Country-level comparisons, Heatmaps, Rankings

---

### 📁 Reference Files

#### 5. `country_mapping.csv`
Mapping between country code formats.

**Columns:**
- `country_code` - ISO-2 (US, MX, BR, ...)
- `iso3` - ISO-3 (USA, MEX, BRA, ...)
- `name` - Full country name
- `region` - Geographic region

---

#### 6. `geo_countries.csv`
Geographic coordinates and metadata.

**Columns:**
- `country` - Full country name
- `lon` - Longitude
- `lat` - Latitude

---

#### 7. `geo_countries.geojson`
**Format:** GeoJSON  
**Contains:** Polygon geometries for each country

**Use for:** Creating choropleth maps with Plotly/Folium

---

## 🔧 Scripts

### Data Collection Scripts

#### `yahoot.py`
Downloads historical cryptocurrency prices from Yahoo Finance.

**Dependencies:**
```python
yfinance, pandas, time
```

**Output:** `crypto_prices_yahoo.csv` → processed into `prices_with_metrics.csv`

**Runtime:** ~2-3 minutes

---

#### `trends.py`
Downloads Google Trends search interest data by country.

**Dependencies:**
```python
pandas, pytrends
```

**Output:** `crypto_trends.csv` → processed into `trends_enriched.csv`

**Runtime:** ~3-5 hours (rate-limited by Google, 30s delay between requests)

**Note:** Script includes retry logic and incremental saving to handle rate limits (429 errors).

---

#### `geodata.py`
Downloads country shapefiles and creates geographic reference data.

**Dependencies:**
```python
geopandas, pandas
```

**Output:** `geo_countries.geojson`, `geo_countries.csv`

**Runtime:** ~1 minute

---

### Data Integration Script

#### `integrate_data.py`
Merges all datasets and calculates derived metrics.

**Dependencies:**
```python
pandas, numpy
```

**Inputs:** `crypto_trends.csv`, `crypto_prices_yahoo.csv`, `geo_countries.csv`

**Outputs:**
- `trends_enriched.csv`
- `prices_with_metrics.csv`
- `integrated_data.csv`
- `country_aggregated.csv`
- `country_mapping.csv`

**Runtime:** ~30 seconds

---

## 📈 Suggested Analyses

### Part 1: Time Series Analysis
**Dataset:** `prices_with_metrics.csv`

**Analyses:**
1. **Random Walk Test** - Test if prices follow random walk (ADF test)
2. **ACF/PACF Analysis** - Autocorrelation of prices, returns, and returns²
3. **Volatility Clustering** - GARCH modeling using `returns_squared`

**Why this dataset?**
- Daily frequency (critical for ACF)
- Complete time series (no gaps)
- Pre-calculated volatility metrics

---

### Part 2: Spatial Analysis
**Datasets:** `trends_enriched.csv` + `geo_countries.geojson`

**Analyses:**
1. **Choropleth Map** - Global interest visualization by country
2. **Regional Time Series** - Interest evolution by region (Americas, Asia, Europe)

**Example (Plotly):**
```python
import plotly.express as px
import pandas as pd

df = pd.read_csv('trends_enriched.csv')
fig = px.choropleth(df, locations='iso3', color='interest',
                    hover_name='name', animation_frame='date')
fig.show()
```

---

### Part 3: Spatiotemporal Integration
**Datasets:** `integrated_data.csv` + `country_aggregated.csv`

**Analyses:**
1. **Correlation Analysis** - Geographic interest vs. global volatility
2. **Lead-Lag Analysis (CCF)** - Does interest predict volatility or vice versa?

**Interpretation:**
- Negative lag: Interest predicts volatility
- Positive lag: Volatility predicts interest
- Lag ≈ 0: Contemporaneous relationship

**Example:**
```python
from statsmodels.tsa.stattools import ccf
import pandas as pd

df = pd.read_csv('integrated_data.csv')
# Filter for one country
us_btc = df[(df['country_code']=='US') & (df['crypto']=='Bitcoin')]

# Cross-correlation
cross_corr = ccf(us_btc['interest'], us_btc['volatility_7d'])
```

---

## 📊 Data Quality Notes

### Temporal Alignment
- **Prices:** Daily data (365 days/year)
- **Trends:** Weekly data (~52 weeks/year)
- **Integrated:** Weekly (limited by trends frequency)

⚠️ **Important:** For time series analysis requiring high frequency (ACF, PACF), use `prices_with_metrics.csv` (daily), NOT `integrated_data.csv` (weekly).

### Missing Data
- **Trends:** Some countries may have weeks with 0 interest (not missing, actual zero)
- **Prices:** Complete daily data, no missing values
- **Coordinates:** All countries have lon/lat values

### Data Interpretation
- **Interest (0-100):** Relative search volume normalized by Google
  - 100 = Peak interest in the time period
  - 50 = Half of peak interest
  - 0 = Less than 1% of peak interest
  
- **Volatility:** Standard deviation of returns
  - Higher values = more price fluctuation
  - Calculated on rolling windows (7d, 30d)

---

## 🚀 Quick Start

```bash
# 1. Download geographic data (1 min)
python geodata.py

# 2. Download trends data (3-5 hours)
python trends.py

# 3. Download price data (2-3 min)
python yahoot.py

# 4. Integrate all datasets (30 sec)
python integrate_data.py
```

---

## 📦 File Size Reference

```
prices_with_metrics.csv    ~1.2 MB
trends_enriched.csv        ~800 KB
integrated_data.csv        ~2.5 MB
country_aggregated.csv     ~5 KB
geo_countries.geojson      ~500 KB
geo_countries.csv          ~2 KB
country_mapping.csv        ~1 KB
```

---

## 🔗 Data Sources

- **Price Data:** [Yahoo Finance](https://finance.yahoo.com) via `yfinance` library
- **Trends Data:** [Google Trends](https://trends.google.com) via `pytrends` library
- **Geographic Data:** [Natural Earth](https://www.naturalearthdata.com/) shapefiles

---

## 📝 License

This dataset is provided for educational and research purposes. Please respect the terms of service of the original data providers (Yahoo Finance, Google Trends).

---

## 👥 Contributing

For questions or issues, please open an issue in the repository.

---

**Last Updated:** October 2025  
**Dataset Version:** 1.0