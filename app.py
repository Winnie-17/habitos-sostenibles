from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habitos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELOS
class HabitoPersonalizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.today)
    datos = db.Column(db.Text)

# RUTAS
@app.route("/")
def index():
    lista = HabitoPersonalizado.query.all()
    registros = Registro.query.order_by(Registro.fecha.desc()).all()
    for r in registros:
        try:
            r.datos = json.loads(r.datos)
        except:
            r.datos = {}
    return render_template("index.html", lista=lista, registros=registros)

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nuevo_habito")
    if nombre:
        db.session.add(HabitoPersonalizado(nombre=nombre))
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/registrar", methods=["POST"])
def registrar():
    lista = HabitoPersonalizado.query.all()
    resultados = {h.nombre: f"habito_{h.id}" in request.form for h in lista}
    nuevo = Registro(datos=json.dumps(resultados), fecha=datetime.today().date())
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    habito = HabitoPersonalizado.query.get_or_404(id)
    db.session.delete(habito)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/aplicaciones")
def aplicaciones():
    return render_template("aplicaciones.html")

@app.route("/reflexion")
def reflexion():
    return render_template("reflexion.html")

@app.route("/codigo")
def codigo():
    return render_template("codigo.html")

with app.app_context():
    db.create_all()

# EJECUCIÓN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
