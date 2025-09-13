from pymongo import MongoClient

# Conexión al MongoDB en Docker
client = MongoClient("mongodb://localhost:27018/")

# Base de datos que vamos a usar
db = client["streaming_db"]


for movie in db["movies"].find():
    print(movie)

for serie in db["series"].find():
    print(serie)
