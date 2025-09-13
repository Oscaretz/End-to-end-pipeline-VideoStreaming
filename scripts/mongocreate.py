from pymongo import MongoClient

# Conexión al MongoDB en Docker
client = MongoClient("mongodb://localhost:27018/")

# Base de datos que vamos a usar
db = client["streaming_db"]

# JSON que quieres insertar
data = {
    "movies": [
        {
            "content_id": "M001",
            "title": "Data Adventures",
            "genre": ["Action", "Sci-Fi"],
            "duration_minutes": 120,
            "release_year": 2023,
            "rating": 4.2,
            "views_count": 15420,
            "production_budget": 50000000
        },
        {
            "content_id": "M002",
            "title": "Analytics Kingdom",
            "genre": ["Fantasy", "Adventure"],
            "duration_minutes": 98,
            "release_year": 2024,
            "rating": 4.5,
            "views_count": 23150,
            "production_budget": 35000000
        }
    ],
    "series": [
        {
            "content_id": "S001",
            "title": "Analytics Chronicles",
            "genre": ["Drama", "Technology"],
            "seasons": 3,
            "episodes_per_season": [10, 12, 8],
            "avg_episode_duration": 45,
            "rating": 4.7,
            "total_views": 89650,
            "production_budget": 120000000
        },
        {
            "content_id": "S002",
            "title": "Data Detectives",
            "genre": ["Crime", "Mystery"],
            "seasons": 2,
            "episodes_per_season": [8, 10],
            "avg_episode_duration": 52,
            "rating": 4.3,
            "total_views": 67420,
            "production_budget": 85000000
        }
    ]
}

# Crear colecciones y insertar datos
movies_collection = db["movies"]
series_collection = db["series"]

movies_collection.insert_many(data["movies"])
series_collection.insert_many(data["series"])

print("✅ Datos insertados en MongoDB!")
