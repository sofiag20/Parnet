from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect
from flask import session, request
from models.Database import Database
from models.Noticia import Noticia
from models.Visita import Visita

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa DB y SocketIO
db = Database.get_instance(app)
socketio = SocketIO(app)

# Variable global para usuarios conectados
usuarios_conectados = set()

@app.route("/")
def index():
    # Noticias
    noticias_query = Noticia.query.order_by(Noticia.id_notice.desc()).limit(5).all()
    noticias_dict = [n.to_dict() for n in noticias_query]

    # Contador de visitas (incrementa al cargar la página)
    visita = Visita.query.first()
    if not visita:
        visita = Visita(total=1)
        db.session.add(visita)
    else:
        visita.total += 1
    db.session.commit()

    return render_template("index.html", noticias=noticias_dict, visitas=visita.total)

# ==========================
# Socket.IO: Conectados en tiempo real
# ==========================

@socketio.on('connect')
def manejar_conexion():
    usuarios_conectados.add(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)

@socketio.on('disconnect')
def manejar_desconexion():
    usuarios_conectados.discard(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)

@app.route("/servicios")
def servicios():
    return render_template("servicios.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

# ==========================
# Ejecutar con socketio.run
# ==========================
if __name__ == "__main__":
    socketio.run(app)


