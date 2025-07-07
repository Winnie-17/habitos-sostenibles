from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habitos.db'
db = SQLAlchemy(app)

class HabitoPersonalizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True)

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    habitos = db.Column(db.Text)

@app.route('/')
def index():
    lista = HabitoPersonalizado.query.order_by(HabitoPersonalizado.id).all()
    registros_raw = Registro.query.order_by(Registro.fecha.desc()).all()
    registros = []
    for r in registros_raw:
        datos = json.loads(r.habitos)
        registros.append({'fecha': r.fecha, 'datos': datos})
    return render_template('index.html', lista=lista, registros=registros)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get('nuevo_habito', '').strip()
    if nombre:
        existente = HabitoPersonalizado.query.filter_by(nombre=nombre).first()
        if not existente:
            nuevo = HabitoPersonalizado(nombre=nombre)
            db.session.add(nuevo)
            db.session.commit()
    return redirect('/')

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    habito = HabitoPersonalizado.query.get_or_404(id)
    db.session.delete(habito)
    db.session.commit()
    return redirect('/')

@app.route('/registrar', methods=['POST'])
def registrar():
    habitos_marcados = {}
    habitos = HabitoPersonalizado.query.all()
    for habito in habitos:
        marcado = request.form.get(f'habito_{habito.id}') == 'on'
        habitos_marcados[habito.nombre] = marcado
    nuevo = Registro(habitos=json.dumps(habitos_marcados))
    db.session.add(nuevo)
    db.session.commit()
    return redirect('/')

@app.route('/aplicaciones')
def aplicaciones():
    return render_template('aplicaciones.html')

@app.route('/reflexion')
def reflexion():
    return render_template('reflexion.html')

@app.route('/codigo')
def codigo():
    return render_template('codigo.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
