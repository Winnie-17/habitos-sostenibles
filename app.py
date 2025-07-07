from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habitos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS DE BASE DE DATOS
class HabitoPersonalizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.today)
    datos = db.Column(db.Text)  # Se almacenan como JSON string

# RUTA PRINCIPAL
@app.route("/")
def index():
    lista = HabitoPersonalizado.query.all()
    registros = Registro.query.order_by(Registro.fecha.desc()).all()

    # Convertir datos JSON a diccionario para mostrar
    for r in registros:
        try:
            r.datos = json.loads(r.datos)
        except:
            r.datos = {}

    return render_template("index.html", lista=lista, registros=registros)

# AGREGAR HÁBITO PERSONALIZADO
@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nuevo_habito")
    if nombre:
        nuevo = HabitoPersonalizado(nombre=nombre)
        db.session.add(nuevo)
        db.session.commit()
    return redirect(url_for('index'))

# REGISTRAR HÁBITOS SELECCIONADOS
@app.route("/registrar", methods=["POST"])
def registrar():
    lista = HabitoPersonalizado.query.all()
    resultados = {}

    for h in lista:
        key = f"habito_{h.id}"
        resultados[h.nombre] = key in request.form

    nuevo_registro = Registro(datos=json.dumps(resultados), fecha=datetime.today().date())
    db.session.add(nuevo_registro)
    db.session.commit()
    return redirect(url_for('index'))

# ELIMINAR HÁBITO
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    habito = HabitoPersonalizado.query.get_or_404(id)
    db.session.delete(habito)
    db.session.commit()
    return redirect(url_for('index'))

# PÁGINAS ADICIONALES
@app.route("/aplicaciones")
def aplicaciones():
    return render_template("aplicaciones.html")

@app.route("/reflexion")
def reflexion():
    return render_template("reflexion.html")

@app.route("/codigo")
def codigo():
    return render_template("codigo.html")

# INICIAR LA APLICACIÓN
if __name__ == "__main__":
    if os.path.exists("habitos.db"):
        os.remove("habitos.db")
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))  # Puerto dinámico para Render
    app.run(host="0.0.0.0", port=port)        # Aceptar conexiones externas
