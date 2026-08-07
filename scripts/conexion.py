import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise ValueError("No se encontró MONGO_URI en el archivo .env")

if not DB_NAME:
    raise ValueError("No se encontró DB_NAME en el archivo .env")

client = MongoClient(MONGO_URI)

# Fuerza la conexión y autenticación real
client.admin.command("ping")

db = client[DB_NAME]

print(f"✅ Conexión y autenticación correctas: {DB_NAME}")