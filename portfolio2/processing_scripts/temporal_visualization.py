"""
Automated Temporal Visualization Generation
Generates time-series visualizations with real data
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

print("=" * 70)
print("AUTOMATED TEMPORAL VISUALIZATION GENERATOR")
print("=" * 70)

# Load data
print("\n📂 Loading data files...")
data_files = {}
try:
    # Try to load all available CSV files
    files_to_load = {
        'integrated': 'integrated_data.csv',
        'trends': 'trends_enriched.csv',
        'aggregated': 'country_aggregated.csv',
        'prices': 'prices_with_metrics.csv',
        'geo': 'geo_countries.csv'
    }

    for key, filename in files_to_load.items():
        try:
            data_files[key] = pd.read_csv(filename)
            print(f"✓ {filename} loaded")
            print(f"  Columns: {data_files[key].columns.tolist()}")
            print(f"  Rows: {len(data_files[key])}")
        except FileNotFoundError:
            print(f"⚠ {filename} not found - skipping")
        except Exception as e:
            print(f"⚠ Error loading {filename}: {e}")

    if not data_files:
        print("✗ No data files could be loaded")
        exit()

except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit()

# Create output directory
import os
os.makedirs('temporal_viz_output', exist_ok=True)
print("✓ Output directory ready: temporal_viz_output/")

# Helper function to find date column
def find_date_column(df):
    """Find the column that contains dates"""
    possible_names = ['date', 'Date', 'datetime', 'time', 'timestamp', 'period']
    for col in df.columns:
        if col.lower() in [n.lower() for n in possible_names]:
            return col
        # Check if column contains date-like data
        try:
            pd.to_datetime(df[col].dropna().iloc[0])
            return col
        except:
            continue
    return None

# Helper function to find country column
def find_country_column(df):
    """Find the column that contains country codes"""
    possible_names = ['country_code', 'country', 'iso', 'iso2', 'iso3', 'code', 'country_iso']
    for col in df.columns:
        if col.lower() in possible_names:
            return col
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].str.len().max() <= 3:
            return col
    return None

# Process temporal data
print("\n🔄 Processing temporal data...")
temporal_data = None
date_col = None
country_col = None

# Find the best dataset for temporal analysis
for key in ['integrated', 'trends', 'prices']:
    if key in data_files:
        df = data_files[key]
        date_col = find_date_column(df)
        country_col = find_country_column(df)

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            df = df.sort_values(date_col)

            if len(df) > 0:
                temporal_data = df
                print(f"✓ Using {key} for temporal analysis")
                print(f"  Date column: {date_col}")
                print(f"  Country column: {country_col}")
                print(f"  Date range: {df[date_col].min()} to {df[date_col].max()}")
                break

if temporal_data is None:
    print("✗ No temporal data found with date column")
    exit()

# Get numeric columns for visualization (exclude geographic coordinates)
all_numeric_cols = temporal_data.select_dtypes(include=[np.number]).columns.tolist()
# Filter out geographic and irrelevant columns
exclude_cols = ['lon', 'lat', 'longitude', 'latitude', 'LABEL_X', 'LABEL_Y']
numeric_cols = [col for col in all_numeric_cols if col.lower() not in [e.lower() for e in exclude_cols]]
print(f"✓ Numeric columns available: {numeric_cols}")
print(f"  (Excluded geographic coordinates: {[c for c in all_numeric_cols if c not in numeric_cols]})")

# Get list of countries
countries = []
if country_col:
    countries = temporal_data[country_col].unique()
    print(f"✓ Countries found: {len(countries)}")
    print(f"  Countries: {', '.join(map(str, countries[:10]))}")

viz_count = 0

# ==========================================
# VIZ 1: Time Series for All Numeric Columns
# ==========================================
print("\n" + "=" * 70)
print("VIZ 1: Time Series Overview (All Metrics)")
print("=" * 70)

if len(numeric_cols) > 0:
    n_metrics = min(4, len(numeric_cols))
    fig, axes = plt.subplots(n_metrics, 1, figsize=(16, 4*n_metrics))
    if n_metrics == 1:
        axes = [axes]

    for idx, col in enumerate(numeric_cols[:n_metrics]):
        ax = axes[idx]

        # Aggregate by date
        daily_data = temporal_data.groupby(date_col)[col].sum().reset_index()

        ax.fill_between(daily_data[date_col], daily_data[col],
                        alpha=0.3, color=f'C{idx}')
        ax.plot(daily_data[date_col], daily_data[col],
                linewidth=2.5, color=f'C{idx}', marker='o', markersize=3)

        ax.set_title(f'{col.replace("_", " ").title()} Over Time',
                     fontsize=13, fontweight='bold')
        ax.set_ylabel(col.replace('_', ' ').title(), fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        if len(daily_data) > 50:
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    axes[-1].set_xlabel('Date', fontsize=12, fontweight='bold')
    fig.suptitle('Temporal Trends Overview', fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/01_overview_timeseries.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 01_overview_timeseries.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 2: Time Series by Country (if country column exists)
# ==========================================
if country_col and len(countries) > 0 and len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 2: Time Series by Country")
    print("=" * 70)

    col = numeric_cols[0]  # Use first numeric column

    fig, ax = plt.subplots(figsize=(16, 9))

    colors = plt.cm.tab20(np.linspace(0, 1, len(countries)))

    for idx, country in enumerate(countries[:20]):  # Limit to 20 countries for clarity
        country_data = temporal_data[temporal_data[country_col] == country]
        if len(country_data) > 0:
            ax.plot(country_data[date_col], country_data[col],
                    marker='o', linewidth=2, markersize=4,
                    label=country, color=colors[idx], alpha=0.8)

    ax.set_title(f'{col.replace("_", " ").title()} by Country Over Time',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.legend(loc='best', ncol=3, fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/02_by_country.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 02_by_country.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 3: Stacked Area Chart (if country data exists)
# ==========================================
if country_col and len(countries) > 1 and len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 3: Stacked Area Chart by Country")
    print("=" * 70)

    col = numeric_cols[0]

    fig, ax = plt.subplots(figsize=(16, 9))

    # Get top countries by total volume
    top_countries = temporal_data.groupby(country_col)[col].sum().nlargest(10).index
    stacked_data = temporal_data[temporal_data[country_col].isin(top_countries)]

    # Pivot data for stacking
    pivot_data = stacked_data.pivot_table(
        index=date_col,
        columns=country_col,
        values=col,
        aggfunc='sum',
        fill_value=0
    )

    ax.stackplot(pivot_data.index,
                 *[pivot_data[col] for col in pivot_data.columns],
                 labels=pivot_data.columns,
                 alpha=0.8)

    ax.set_title(f'{col.replace("_", " ").title()} Distribution (Top 10 Countries)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', ncol=2, fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/03_stacked_area.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 03_stacked_area.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 4: Heatmap - Monthly Patterns
# ==========================================
if country_col and len(countries) > 1 and len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 4: Heatmap - Temporal Patterns")
    print("=" * 70)

    col = numeric_cols[0]

    fig, ax = plt.subplots(figsize=(16, 10))

    # Get top countries
    top_countries = temporal_data.groupby(country_col)[col].mean().nlargest(15).index
    heatmap_data = temporal_data[temporal_data[country_col].isin(top_countries)].copy()

    # Create time periods (weekly or monthly depending on data volume)
    if len(temporal_data) > 500:
        heatmap_data['period'] = heatmap_data[date_col].dt.to_period('M')
    else:
        heatmap_data['period'] = heatmap_data[date_col].dt.to_period('W')

    # Create pivot table
    pivot = heatmap_data.pivot_table(
        index=country_col,
        columns='period',
        values=col,
        aggfunc='mean'
    )

    im = ax.imshow(pivot.values, aspect='auto', cmap='RdYlGn', interpolation='nearest')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(col) for col in pivot.columns], rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)

    ax.set_title(f'{col.replace("_", " ").title()} Heatmap (by Country & Period)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Period', fontsize=12, fontweight='bold')
    ax.set_ylabel('Country', fontsize=12, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(col.replace('_', ' ').title(), rotation=270, labelpad=20, fontweight='bold')

    plt.tight_layout()
    plt.savefig('temporal_viz_output/04_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 04_heatmap.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 5: Small Multiples - Top Countries
# ==========================================
if country_col and len(countries) >= 4 and len(numeric_cols) >= 1:
    print("\n" + "=" * 70)
    print("VIZ 5: Small Multiples - Individual Country Trends")
    print("=" * 70)

    col = numeric_cols[0]

    # Get top 9 countries
    top_countries = temporal_data.groupby(country_col)[col].sum().nlargest(9).index

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, country in enumerate(top_countries):
        country_data = temporal_data[temporal_data[country_col] == country]
        ax = axes[idx]

        # Plot main metric
        ax.fill_between(country_data[date_col], country_data[col],
                       alpha=0.3, color='#3498db')
        ax.plot(country_data[date_col], country_data[col],
               linewidth=2, color='#2c3e50', marker='o', markersize=3)

        # If there's a second metric, plot it on secondary axis
        if len(numeric_cols) > 1:
            ax2 = ax.twinx()
            col2 = numeric_cols[1]
            ax2.plot(country_data[date_col], country_data[col2],
                    linewidth=2, color='#e74c3c', marker='s', markersize=3, alpha=0.7)
            ax2.set_ylabel(col2.replace('_', ' ')[:15], fontsize=8, color='#e74c3c')
            ax2.tick_params(axis='y', labelcolor='#e74c3c', labelsize=7)

        ax.set_title(str(country), fontsize=11, fontweight='bold')
        ax.set_ylabel(col.replace('_', ' ')[:15], fontsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=7)

        if idx >= 6:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=7)
        else:
            ax.set_xticklabels([])

    fig.suptitle(f'{col.replace("_", " ").title()} by Country',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('temporal_viz_output/05_small_multiples.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 05_small_multiples.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 6: Latest Period Comparison
# ==========================================
if country_col and len(countries) > 0 and len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 6: Latest Period Comparison")
    print("=" * 70)

    # Get most recent period
    latest_date = temporal_data[date_col].max()
    recent_data = temporal_data[temporal_data[date_col] == latest_date]

    # Determine number of subplots
    n_plots = min(4, len(numeric_cols))
    fig, axes = plt.subplots(2, 2, figsize=(16, 12)) if n_plots >= 4 else plt.subplots(1, n_plots, figsize=(8*n_plots, 6))

    if n_plots == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if n_plots >= 4 else axes

    for idx, col in enumerate(numeric_cols[:n_plots]):
        ax = axes[idx]

        data = recent_data.sort_values(col, ascending=False).head(10)
        bars = ax.barh(data[country_col], data[col], color=f'C{idx}', alpha=0.8)

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f}',
                    ha='left', va='center', fontsize=9, fontweight='bold')

        ax.set_title(f'{col.replace("_", " ").title()} - {latest_date.strftime("%Y-%m-%d")}',
                     fontsize=12, fontweight='bold')
        ax.set_xlabel(col.replace('_', ' ').title(), fontsize=10)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')

    fig.suptitle('Latest Period Comparison (Top 10 Countries)',
                 fontsize=16, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/06_latest_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 06_latest_comparison.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 7: Rolling Average / Trend Analysis
# ==========================================
if len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 7: Trend Analysis with Rolling Average")
    print("=" * 70)

    col = numeric_cols[0]

    fig, ax = plt.subplots(figsize=(16, 9))

    # Aggregate by date
    daily_data = temporal_data.groupby(date_col)[col].sum().reset_index()

    # Calculate rolling average
    window = min(7, len(daily_data) // 10) if len(daily_data) > 20 else 3
    daily_data['rolling_avg'] = daily_data[col].rolling(window=window, center=True).mean()

    # Plot original data
    ax.plot(daily_data[date_col], daily_data[col],
            linewidth=1, color='#95a5a6', marker='o', markersize=3,
            alpha=0.5, label='Actual')

    # Plot rolling average
    ax.plot(daily_data[date_col], daily_data['rolling_avg'],
            linewidth=3, color='#e74c3c', label=f'{window}-period Moving Average')

    ax.set_title(f'{col.replace("_", " ").title()} - Trend Analysis',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel(col.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/07_trend_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 07_trend_analysis.png")
    plt.close()
    viz_count += 1

# ==========================================
# VIZ 8: Month-over-Month Change
# ==========================================
if len(numeric_cols) > 0:
    print("\n" + "=" * 70)
    print("VIZ 8: Period-over-Period Change Analysis")
    print("=" * 70)

    col = numeric_cols[0]

    fig, ax = plt.subplots(figsize=(16, 9))

    # Aggregate by date and calculate change
    daily_data = temporal_data.groupby(date_col)[col].sum().reset_index()
    daily_data['change'] = daily_data[col].pct_change() * 100

    # Remove first row (NaN)
    change_data = daily_data[daily_data['change'].notna()]

    # Color bars based on positive/negative
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in change_data['change']]

    ax.bar(change_data[date_col], change_data['change'],
           color=colors, alpha=0.7, edgecolor='#2c3e50', linewidth=0.5)

    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)

    ax.set_title(f'{col.replace("_", " ").title()} - Period-over-Period % Change',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('% Change', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig('temporal_viz_output/08_change_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 08_change_analysis.png")
    plt.close()
    viz_count += 1

# ==========================================
# Summary
# ==========================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✓ Countries analyzed: {len(countries) if len(countries) > 0 else 'N/A'}")
print(f"✓ Numeric variables visualized: {len(numeric_cols)}")
print(f"✓ Date range: {temporal_data[date_col].min()} to {temporal_data[date_col].max()}")
print(f"✓ Total data points: {len(temporal_data)}")
print(f"✓ All visualizations saved to: temporal_viz_output/")

# List all created files
created_files = sorted([f for f in os.listdir('temporal_viz_output') if f.endswith('.png')])
print(f"\n📊 Generated {len(created_files)} visualizations:")
for i, filename in enumerate(created_files, 1):
    print(f"  {i}. {filename}")

print("\n🎉 Temporal visualization generation complete!")