from flask import Flask, render_template,redirect, url_for, flash,jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask import session, request
from models.Database import Database
from models.Noticia import Noticia
from models.Visita import Visita
from models.Usuario import Usuario

app = Flask(__name__)
app.secret_key = "admin123"
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


@socketio.on('connect')
def manejar_conexion():
    usuarios_conectados.add(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)

@socketio.on('disconnect')
def manejar_desconexion():
    usuarios_conectados.discard(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)


@app.route("/contenido/principal")
def contenido_principal():
    return render_template("fragmentos/principal.html")

@app.route("/contenido/quienes")
def contenido_quienes():
    return render_template("fragmentos/quienes.html")

@app.route("/contenido/clientes")
def contenido_clientes():
    return render_template("fragmentos/clientes.html")



@app.route("/servicios")
def servicios():
    return render_template("servicios.html")


@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/contenido/admin")
def contenido_admin():
    if session.get("rol") == "admin":
        return render_template("fragmentos/admin.html")
    return "No autorizado", 403




@app.route("/contenido/login")
def contenido_login():
    return render_template("fragmentos/login.html")

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user")
    pw = request.form.get("pw")

    usuario = Usuario.query.filter_by(user=user).first()

    if usuario and usuario.pw == pw:
        session["usuario_id"] = usuario.id
        session["rol"] = usuario.rol
        return jsonify({"success": True, "rol": usuario.rol})
    else:
        return jsonify({"success": False, "message": "Credenciales inválidas"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    socketio.run(app)


