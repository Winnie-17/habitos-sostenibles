from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habitos.db'
db = SQLAlchemy(app)

class HabitoPersonalizado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    usuario = db.Column(db.String(100))  # Nuevo: cada hábito está asociado a un usuario

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.today)
    datos = db.Column(db.Text)  # json.dumps()
    usuario = db.Column(db.String(100))  # Nuevo: cada registro está asociado a un usuario

@app.before_request
def set_usuario():
    if request.endpoint != 'inicio' and 'usuario' not in session:
        return redirect(url_for('inicio'))

@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        if nombre:
            session['usuario'] = nombre
            return redirect(url_for('index'))
    return render_template('inicio.html')

@app.route('/index')
def index():
    usuario = session['usuario']
    lista = HabitoPersonalizado.query.filter_by(usuario=usuario).all()
    registros = Registro.query.filter_by(usuario=usuario).order_by(Registro.fecha.desc()).all()
    return render_template('index.html', lista=lista, registros=[{
        'fecha': r.fecha,
        'datos': json.loads(r.datos)
    } for r in registros])

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nuevo_habito'].strip()
    if nombre:
        nuevo = HabitoPersonalizado(nombre=nombre, usuario=session['usuario'])
        db.session.add(nuevo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    habito = HabitoPersonalizado.query.get(id)
    if habito and habito.usuario == session['usuario']:
        db.session.delete(habito)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/registrar', methods=['POST'])
def registrar():
    datos = {}
    for key in request.form:
        if key.startswith('habito_'):
            habito_id = int(key.split('_')[1])
            habito = HabitoPersonalizado.query.get(habito_id)
            if habito and habito.usuario == session['usuario']:
                datos[habito.nombre] = True
    registro = Registro(datos=json.dumps(datos), usuario=session['usuario'])
    db.session.add(registro)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
