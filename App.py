# App.py
from flask import (
    Flask, render_template, redirect, url_for,
    session, request
)
from flask_socketio import SocketIO, emit
from models.Database import Database
from models.Noticia   import Noticia
from models.Visita    import Visita
from models.Usuario   import Usuario
from models.Producto  import Producto

# Instancia única de SQLAlchemy
db = Database.get_instance()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "admin123"
app.config['SQLALCHEMY_DATABASE_URI']        = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Asociamos db y SocketIO
db.init_app(app)
socketio = SocketIO(app)

# Mantiene los sid de usuarios conectados
usuarios_conectados = set()

# ——————————————————————————————
# RUTAS PÚBLICAS
# ——————————————————————————————

@app.route("/")
def index():
    noticias = Noticia.query \
        .order_by(Noticia.id_notice.desc()) \
        .limit(5) \
        .all()
    visita = Visita.query.first()
    if not visita:
        visita = Visita(total=1)
        db.session.add(visita)
    else:
        visita.total += 1
    db.session.commit()

    return render_template(
        "index.html",
        noticias=[n.to_dict() for n in noticias],
        visitas=visita.total
    )

# Fragmentos cargados por AJAX
@app.route("/contenido/principal")
def contenido_principal():
    return render_template("fragmentos/principal.html")

@app.route("/contenido/quienes")
def contenido_quienes():
    return render_template("fragmentos/quienes.html")

@app.route("/contenido/clientes")
def contenido_clientes():
    return render_template("fragmentos/clientes.html")

# Páginas completas estáticas
@app.route("/servicios")
def servicios():
    return render_template("servicios.html")

@app.route("/contenido/productos")
def productos():
    q = request.args.get('q', '').strip()
    if q:
        # Buscamos en el campo descripción
        productos = Producto.query.filter(
            Producto.descripcion.ilike(f'%{q}%')
        ).all()
    else:
        productos = Producto.query.all()
    return render_template('fragmentos/producto.html', productos=productos)

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

# ——————————————————————————————
# SOCKET.IO PARA USUARIOS CONECTADOS
# ——————————————————————————————

@socketio.on('connect')
def manejar_conexion():
    usuarios_conectados.add(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)

@socketio.on('disconnect')
def manejar_desconexion():
    usuarios_conectados.discard(request.sid)
    emit('actualizar_conectados', len(usuarios_conectados), broadcast=True)

# ——————————————————————————————
# LOGIN / LOGOUT
# ——————————————————————————————

@app.route("/login2")
def login2():
    # Antes: return render_template("Login2.html")
    return render_template("login2.html")


@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("user")
    pw   = request.form.get("pw")
    usuario = Usuario.query.filter_by(user=user).first()
    if usuario and usuario.pw == pw:
        session["usuario_id"] = usuario.id
        session["rol"]        = usuario.rol
        return redirect(url_for("productos_admin2"))
    return redirect(url_for("login2"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login2"))

# ——————————————————————————————
# ADMINISTRACIÓN DE PRODUCTOS (CRUD EN PÁGINA COMPLETA)
# ——————————————————————————————

@app.route("/productos_admin2")
def productos_admin2():
    if session.get("rol") != "admin":
        return redirect(url_for("login2"))
    productos = Producto.query.all()
    return render_template("productos_admin2.html", productos=productos)

@app.route("/admin/producto/crear", methods=["POST"])
def crear_producto():
    descripcion = request.form["descripcion"]
    costo       = request.form["costo"]
    stock       = request.form["stock"]
    imagen      = request.form.get("imagen")
    nuevo = Producto(
        descripcion=descripcion,
        costo=costo,
        stock=stock,
        imagen=imagen
    )
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("productos_admin2"))

@app.route("/admin/producto/editar/<int:id>", methods=["POST"])
def editar_producto(id):
    p = Producto.query.get_or_404(id)
    p.descripcion = request.form["descripcion"]
    p.costo       = request.form["costo"]
    p.stock       = request.form["stock"]
    p.imagen      = request.form.get("imagen")
    db.session.commit()
    return redirect(url_for("productos_admin2"))

@app.route("/admin/producto/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("productos_admin2"))



# ——————————————————————————————
# EJECUCIÓN
# ——————————————————————————————

if __name__ == "__main__":
    # Arranca HTTP + WebSocket
    socketio.run
