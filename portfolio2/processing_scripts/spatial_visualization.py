"""
Automated Spatial Visualization Generation
Generates multiple map visualizations from geographic data
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

print("=" * 70)
print("AUTOMATED SPATIAL VISUALIZATION GENERATOR")
print("=" * 70)

# Load data
print("\n📂 Loading geographic data...")
try:
    # Load GeoJSON
    geo_countries = gpd.read_file('geo_countries.geojson')
    print("✓ GeoJSON loaded")
    print(f"  Columns: {geo_countries.columns.tolist()}")

    # Load country mapping
    country_mapping = pd.read_csv('country_mapping.csv')
    print("✓ Country mapping loaded")
    print(f"  Columns: {country_mapping.columns.tolist()}")

    # Load aggregated data
    aggregated = pd.read_csv('country_aggregated.csv')
    print("✓ Aggregated data loaded")
    print(f"  Columns: {aggregated.columns.tolist()}")

    # Load integrated data
    integrated = pd.read_csv('integrated_data.csv')
    print("✓ Integrated data loaded")
    print(f"  Columns: {integrated.columns.tolist()}")

    # Try to load base world map from URL
    try:
        world = gpd.read_file("https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip")
        print("✓ Base world map loaded from Natural Earth")
    except:
        print("⚠ Using simplified world map")
        world = geo_countries.copy()

except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit()

# Create output directory for maps
import os
os.makedirs('maps_output', exist_ok=True)
print("✓ Output directory ready: maps_output/")

# Identify the country code column in each dataframe
def find_country_column(df):
    """Find the column that contains country codes"""
    possible_names = ['country_code', 'country', 'iso', 'iso2', 'iso3', 'code', 'country_iso']
    for col in df.columns:
        if col.lower() in possible_names:
            return col
    # If no match, return first column that looks like a country code
    for col in df.columns:
        if df[col].dtype == 'object' and df[col].str.len().max() <= 3:
            return col
    return df.columns[0]

geo_country_col = find_country_column(geo_countries)
agg_country_col = find_country_column(aggregated)

print(f"\n🔍 Identified columns:")
print(f"  GeoJSON country column: {geo_country_col}")
print(f"  Aggregated country column: {agg_country_col}")

# Merge geographic data with aggregated metrics
geo_with_data = geo_countries.merge(
    aggregated,
    left_on=geo_country_col,
    right_on=agg_country_col,
    how='left'
)

print(f"  Merged data has {len(geo_with_data)} rows")

# Find numeric columns for visualization
numeric_cols = aggregated.select_dtypes(include=[np.number]).columns.tolist()
print(f"  Available numeric columns: {numeric_cols}")

# ==========================================
# MAP 1: Basic Country Boundaries
# ==========================================
print("\n" + "=" * 70)
print("MAP 1: Basic Country Boundaries")
print("=" * 70)

fig, ax = plt.subplots(figsize=(20, 12))

# Plot world background
if len(world) > len(geo_countries):
    world.plot(ax=ax, color='#ecf0f1', edgecolor='#95a5a6', linewidth=0.5)

# Plot selected countries
geo_countries.plot(ax=ax, color='#3498db', edgecolor='#2c3e50', linewidth=1.5, alpha=0.8)

ax.set_title('Selected Countries - Geographic Coverage', fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('maps_output/01_basic_boundaries.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 01_basic_boundaries.png")
plt.close()

# ==========================================
# MAP 2: Countries with Labels
# ==========================================
print("\n" + "=" * 70)
print("MAP 2: Countries with Labels")
print("=" * 70)

fig, ax = plt.subplots(figsize=(20, 12))

# Plot world background
if len(world) > len(geo_countries):
    world.plot(ax=ax, color='#ecf0f1', edgecolor='#95a5a6', linewidth=0.5)

# Plot selected countries
geo_countries.plot(ax=ax, color='#2ecc71', edgecolor='#27ae60', linewidth=1.5, alpha=0.7)

# Add country labels
for idx, row in geo_countries.iterrows():
    try:
        centroid = row.geometry.centroid
        label = row[geo_country_col]
        ax.annotate(label,
                    xy=(centroid.x, centroid.y),
                    fontsize=11,
                    fontweight='bold',
                    ha='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                             edgecolor='#2ecc71', alpha=0.9),
                    zorder=6)
    except:
        continue

ax.set_title('Countries with Country Codes', fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Longitude', fontsize=12)
ax.set_ylabel('Latitude', fontsize=12)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('maps_output/02_countries_labeled.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 02_countries_labeled.png")
plt.close()

# ==========================================
# MAP 3+: Choropleth Maps for Numeric Columns
# ==========================================
print("\n" + "=" * 70)
print("MAPS 3+: Choropleth Maps for Numeric Variables")
print("=" * 70)

map_number = 3
for col in numeric_cols[:4]:  # Limit to first 4 numeric columns
    if col == agg_country_col:
        continue

    print(f"\nCreating choropleth for: {col}")

    # Skip if all NaN
    if geo_with_data[col].isna().all():
        print(f"  Skipping {col} - all values are NaN")
        continue

    fig, ax = plt.subplots(figsize=(20, 12))

    # Plot world background
    if len(world) > len(geo_countries):
        world.plot(ax=ax, color='#ecf0f1', edgecolor='#95a5a6', linewidth=0.5)

    # Choose colormap based on values
    if geo_with_data[col].min() < 0:
        cmap = 'RdYlGn'
    else:
        cmap = 'YlOrRd'

    # Plot choropleth
    geo_with_data.plot(ax=ax, column=col, cmap=cmap,
                        edgecolor='#2c3e50', linewidth=1.5,
                        legend=True, alpha=0.8,
                        legend_kwds={'label': col.replace('_', ' ').title(),
                                    'orientation': 'horizontal',
                                    'shrink': 0.5},
                        missing_kwds={'color': 'lightgrey', 'label': 'No data'})

    # Add country labels with values
    for idx, row in geo_with_data.iterrows():
        try:
            centroid = row.geometry.centroid
            if pd.notna(row[col]):
                value = row[col]
                label_text = f"{row[geo_country_col]}\n{value:.1f}"
                ax.annotate(label_text,
                            xy=(centroid.x, centroid.y),
                            fontsize=9,
                            fontweight='bold',
                            ha='center',
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        except:
            continue

    title = f'{col.replace("_", " ").title()} by Country'
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')

    filename = f'{map_number:02d}_choropleth_{col}.png'
    plt.tight_layout()
    plt.savefig(f'maps_output/{filename}', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {filename}")
    plt.close()

    map_number += 1

# ==========================================
# MAP: Bubble Map if we have 2+ numeric columns
# ==========================================
if len(numeric_cols) >= 2:
    print("\n" + "=" * 70)
    print(f"MAP {map_number}: Bubble Map - Multiple Metrics")
    print("=" * 70)

    col1, col2 = numeric_cols[0], numeric_cols[1]

    # Filter out NaN values
    bubble_data = geo_with_data.dropna(subset=[col1, col2])

    if len(bubble_data) > 0:
        fig, ax = plt.subplots(figsize=(20, 12))

        # Plot world background
        if len(world) > len(geo_countries):
            world.plot(ax=ax, color='#2c3e50', edgecolor='#34495e', linewidth=0.5)

        # Plot selected countries
        geo_countries.plot(ax=ax, color='#34495e', edgecolor='#7f8c8d', linewidth=1, alpha=0.5)

        # Plot bubbles for each country
        for idx, row in bubble_data.iterrows():
            try:
                centroid = row.geometry.centroid

                # Size based on first metric, color based on second
                size = (row[col1] / bubble_data[col1].max()) * 3000
                color_val = (row[col2] - bubble_data[col2].min()) / (bubble_data[col2].max() - bubble_data[col2].min())

                ax.scatter(centroid.x, centroid.y,
                          s=size,
                          c=[color_val],
                          cmap='RdYlGn',
                          alpha=0.7,
                          edgecolors='white',
                          linewidth=2,
                          vmin=0, vmax=1,
                          zorder=5)

                ax.annotate(row[geo_country_col],
                            xy=(centroid.x, centroid.y),
                            fontsize=10,
                            fontweight='bold',
                            color='white',
                            ha='center',
                            va='center',
                            zorder=6)
            except:
                continue

        title = f'{col1.replace("_", " ").title()} vs {col2.replace("_", " ").title()}\n(Size={col1}, Color={col2})'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20, color='white')
        ax.set_xlabel('Longitude', fontsize=12, color='white')
        ax.set_ylabel('Latitude', fontsize=12, color='white')
        ax.tick_params(colors='white')
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#1a1a1a')

        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap='RdYlGn',
                                    norm=plt.Normalize(vmin=bubble_data[col2].min(),
                                                      vmax=bubble_data[col2].max()))
        sm._A = []
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label(col2.replace('_', ' ').title(), rotation=270, labelpad=20,
                      fontweight='bold', color='white')
        cbar.ax.tick_params(colors='white')

        filename = f'{map_number:02d}_bubble_map.png'
        plt.tight_layout()
        plt.savefig(f'maps_output/{filename}', dpi=300, bbox_inches='tight',
                    facecolor='#1a1a1a')
        print(f"✓ Saved: {filename}")
        plt.close()

        map_number += 1

# ==========================================
# Summary
# ==========================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✓ Countries visualized: {len(geo_countries)}")
print(f"✓ Numeric variables mapped: {len(numeric_cols)}")
print(f"✓ All maps saved to: maps_output/")

# List all created files
created_files = sorted([f for f in os.listdir('maps_output') if f.endswith('.png')])
print(f"\n📊 Generated {len(created_files)} maps:")
for i, filename in enumerate(created_files, 1):
    print(f"  {i}. {filename}")

print("\n🎉 Spatial visualization generation complete!")