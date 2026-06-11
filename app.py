import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
from bson import ObjectId
from dotenv import load_dotenv


base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

from database import db  



base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

if not os.path.exists(template_dir) and os.path.exists(os.path.join(base_dir, 'Templates')):
    template_dir = os.path.join(base_dir, 'Templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv("SECRET_KEY", "KattySecretBackup2026")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión primero.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTA 1: LOGIN 
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password_plana = request.form.get("password")
        
        if not email or not password_plana:
            flash("Por favor llena todos los campos.", "warning")
            return redirect(url_for("login"))
            
        # Buscar usuario en MongoDB
        usuario = db.usuarios.find_one({"email": email})
        
        # Verificar si existe y la contraseña coincide
        if usuario and bcrypt.checkpw(password_plana.encode('utf-8'), usuario["password"]):
            session["usuario_id"] = str(usuario["_id"])
            session["usuario_email"] = usuario["email"]
            flash("¡Bienvenido al sistema!", "success")
            return redirect(url_for("listar_mascotas"))
        else:
            flash("Credenciales incorrectas.", "danger")
            
    return render_template("login.html")

# --- RUTA 2: REGISTRO DE USUARIOS ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password_plana = request.form.get("password")
        
        if not email or not password_plana:
            flash("Todos los campos son obligatorios.", "warning")
            return redirect(url_for("registro"))
            
        # Verificar si el usuario ya existe
        usuario_existente = db.usuarios.find_one({"email": email})
        if usuario_existente:
            flash("El correo electrónico ya está registrado.", "danger")
            return redirect(url_for("registro"))
            
        try:
            # Hashear la contraseña antes de guardarla
            password_hasheada = bcrypt.hashpw(password_plana.encode('utf-8'), bcrypt.gensalt())
            
            db.usuarios.insert_one({
                "email": email,
                "password": password_hasheada
            })
            flash("Usuario registrado con éxito. ¡Ya puedes iniciar sesión!", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            flash(f"Error al registrar en MongoDB: {e}", "danger")
            
    return render_template("registro.html")

# --- RUTA 3: LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("login"))

# ==========================================
#          CRUD ENTIDAD 1: MASCOTAS
# ==========================================

# LEER
@app.route("/mascotas")
@login_required
def listar_mascotas():
    lista_mascotas = list(db.mascotas.find({"activo": True}))
    return render_template("mascotas.html", mascotas=lista_mascotas)

# CREAR
@app.route("/mascotas/crear", methods=["POST"])
@login_required
def crear_mascota():
    nombre = request.form.get("nombre").strip()
    especie = request.form.get("especie").strip()
    edad = request.form.get("edad")
    
    if not nombre or not especie or not edad:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for("listar_mascotas"))
        
    try:
        db.mascotas.insert_one({
            "nombre": nombre,
            "especie": especie,
            "edad": int(edad),
            "activo": True  
        })
        flash("Mascota registrada con éxito.", "success")
    except Exception as e:
        flash(f"Error de validación en MongoDB: {e}", "danger")
        
    return redirect(url_for("listar_mascotas"))

# EDITAR
@app.route("/mascotas/editar/<id>", methods=["POST"])
@login_required
def editar_mascota(id):
    nombre = request.form.get("nombre").strip()
    especie = request.form.get("especie").strip()
    edad = request.form.get("edad")
    
    try:
        db.mascotas.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "nombre": nombre,
                "especie": especie,
                "edad": int(edad)
            }}
        )
        flash("Mascota actualizada correctamente.", "success")
    except Exception as e:
        flash(f"No se pudo actualizar: {e}", "danger")
        
    return redirect(url_for("listar_mascotas"))

# BORRAR (Borrado Lógico)
@app.route("/mascotas/borrar/<id>")
@login_required
def borrar_mscota(id):
    try:
        db.mascotas.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"activo": False}}
        )
        flash("Mascota desactivada del sistema (Borrado lógico).", "success")
    except Exception as e:
        flash(f"Error al desactivar: {e}", "danger")
    return redirect(url_for("listar_mascotas"))


# ==========================================
#          CRUD ENTIDAD 2: CONSULTAS
# ==========================================

@app.route("/consultas")
@login_required
def listar_consultas():
    pipeline = [
        {
            "$lookup": {
                "from": "mascotas",
                "localField": "mascota_id",
                "foreignField": "_id",
                "as": "datos_mascota"
            }
        },
        {
            "$match": {
                "datos_mascota.activo": True
            }
        }
    ]
    lista_consultas = list(db.consultas.aggregate(pipeline))
    lista_mascotas = list(db.mascotas.find({"activo": True})) 
    
    return render_template("consultas.html", consultas=lista_consultas, mascotas=lista_mascotas)

# CREAR CONSULTA
@app.route("/consultas/crear", methods=["POST"])
@login_required
def crear_consulta():
    mascota_id = request.form.get("mascota_id")
    fecha = request.form.get("fecha")
    motivo = request.form.get("motivo").strip()
    diagnostico = request.form.get("diagnostico").strip()
    
    if not mascota_id or not fecha or not motivo:
        flash("Llena los campos obligatorios.", "danger")
        return redirect(url_for("listar_consultas"))
        
    db.consultas.insert_one({
        "mascota_id": ObjectId(mascota_id),
        "fecha": fecha,
        "motivo": motivo,
        "diagnostico": diagnostico
    })
    flash("Consulta agregada con éxito.", "success")
    return redirect(url_for("listar_consultas"))

# BORRAR CONSULTA
@app.route("/consultas/borrar/<id>")
@login_required
def borrar_consulta(id):
    db.consultas.delete_one({"_id": ObjectId(id)})
    flash("Consulta eliminada.", "success")
    return redirect(url_for("listar_consultas"))


if __name__ == "__main__":
    app.run(debug=True)
