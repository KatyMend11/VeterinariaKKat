import sys
import os
import bcrypt
from bson import ObjectId

if 'database' in sys.modules:
    del sys.modules['database']

from database import db, init_db

def run_seed():
    print("Conectando y limpiando base de datos en MongoDB 8...")
    
    
    db.usuarios.drop()
    db.mascotas.drop()
    db.consultas.drop()
    
    
    init_db()
     
    password_plana = "Demo1234" 
    password_hasheada = bcrypt.hashpw(password_plana.encode('utf-8'), bcrypt.gensalt())
    
    db.usuarios.insert_one({
        "email": "demo@demo.com", 
        "password": password_hasheada
    })
    print("👤 Usuario Demo creado con éxito.")

    
    # 2. Insertar Mascotas de ejemplo con estado activo
    mascota1_id = db.mascotas.insert_one({
        "nombre": "Max",
        "especie": "Perro",
        "edad": int(4),
        "activo": True 
    }).inserted_id

    db.mascotas.insert_one({
        "nombre": "Luna",
        "especie": "Gato",
        "edad": int(2),
        "activo": True  
    })
    print("🐾 Mascotas semilla insertadas.")

    
    db.consultas.insert_one({
        "mascota_id": mascota1_id, 
        "fecha": "2026-06-10",
        "motivo": "Vacunación anual",
        "diagnostico": "Saludable. Se aplica séptuple."
    })
    print("Consultas semilla insertadas.")
    print("Seed completado con éxito. Los datos ya están persistidos en la nube.")

if __name__ == "__main__":
    run_seed()