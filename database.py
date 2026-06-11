import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


client = MongoClient(os.getenv("MONGODB_URI"))


db = client["veterinaria_db"]

def init_db():
    
    db.usuarios.create_index("email", unique=True)
    
    # Validación de Esquema Nativa para la colección 'mascotas'
    mascota_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["nombre", "especie", "edad"],
            "properties": {
                "nombre": {
                    "bsonType": "string",
                    "description": "Debe ser un string y es requerido"
                },
                "especie": {
                    "bsonType": "string",
                    "description": "Debe ser 'Perro', 'Gato', etc."
                },
                "edad": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "Debe ser un entero mayor o igual a 0"
                }
            }
        }
    }
    
    # Aplicar la validación a la colección
    if "mascotas" not in db.list_collection_names():
        db.create_collection("mascotas", validator=mascota_validator)
    else:
        db.command("collMod", "mascotas", validator=mascota_validator)
