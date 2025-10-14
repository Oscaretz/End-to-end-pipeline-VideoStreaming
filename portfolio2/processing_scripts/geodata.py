import geopandas as gpd
import pandas as pd

# === Cargar shapefile mundial ===
world = gpd.read_file("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip")

# Mostrar las columnas para identificar el nombre del país
print("🗺️ Columnas disponibles en el shapefile:")
print(world.columns.tolist())

# Detectar columna con nombre de país
country_col = None
for possible in ["name", "NAME", "ADMIN", "SOVEREIGNT", "NAME_EN"]:
    if possible in world.columns:
        country_col = possible
        break

if country_col is None:
    raise ValueError("❌ No se encontró ninguna columna con el nombre del país en el shapefile.")

print(f"✅ Se usará la columna '{country_col}' para unir los datos.\n")

# === Coordenadas de capitales ===
capitals = {
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

geo_df = pd.DataFrame({
    "country": list(capitals.keys()),
    "lon": [v[0] for v in capitals.values()],
    "lat": [v[1] for v in capitals.values()]
})

# === Convertir a GeoDataFrame ===
geo_gdf = gpd.GeoDataFrame(
    geo_df, geometry=gpd.points_from_xy(geo_df.lon, geo_df.lat), crs="EPSG:4326"
)

# === Unir usando la columna detectada ===
geo_merged = world.merge(geo_df, left_on=country_col, right_on="country", how="inner")

# === Guardar archivos ===
geo_merged.to_file("geo_countries.geojson", driver="GeoJSON")
geo_merged.to_csv("geo_countries.csv", index=False)

print("✅ Archivos creados correctamente:")
print("- geo_countries.geojson")
print("- geo_countries.csv")

print("\n📊 Vista previa:")
print(geo_merged[["country", "lon", "lat"]].head())
