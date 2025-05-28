import smtplib   
import os
from flask import (
    Flask, render_template, redirect, url_for,
    session, request, current_app, flash
)
from flask_socketio import SocketIO, emit
from models.Database import Database
from models.Noticia   import Noticia
from models.Visita    import Visita
from models.Usuario   import Usuario
from models.Producto  import Producto
from models.Contacto import ContactoForm
from email.mime.text import MIMEText

# Instancia única de SQLAlchemy
db = Database.get_instance()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "admin123"
app.config['SQLALCHEMY_DATABASE_URI']        = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = '4338b5a9e5c318f36ecc450a84236f2edb254dea3a2ee6ff'


# Datos de tu servidor SMTP
app.config['SMTP_SERVER']       = 'smtp.gmail.com'  
app.config['SMTP_PORT']         = 587    
app.config['SMTP_USER']         = 'parnetoficial@gmail.com' 
app.config['SMTP_PASS']         = 'gfss tlhm nhpb dvde'


# Destinatario del formulario de contacto
app.config['CONTACT_RECIPIENT'] = 'parnetoficial@gmail.com' 

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

@app.route('/contenido/contacto', methods=['GET', 'POST'])
def contenido_contacto():
    form = ContactoForm()
    return render_template('fragmentos/contacto.html', form=form)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        # 1) Leer campos del formulario
        nombre  = request.form.get('nombre', '').strip()
        correo  = request.form.get('correo', '').strip()
        asunto  = request.form.get('asunto', '').strip()
        mensaje = request.form.get('mensaje', '').strip()

        # 2) Validación mínima
        if not nombre or not correo or not asunto or not mensaje:
            flash('Por favor completa todos los campos.', 'danger')
            return redirect(url_for('contacto'))

        # 3) Construir el cuerpo del mensaje
        cuerpo = f"""De: {nombre} <{correo}>

Asunto: {asunto}

Mensaje:
{mensaje}
"""

        # 4) Crear el objeto MIMEText
        msg = MIMEText(cuerpo, _charset='utf-8')
        msg['Subject']  = asunto
        msg['From']     = current_app.config['SMTP_USER']
        msg['To']       = current_app.config['CONTACT_RECIPIENT']
        msg['Reply-To'] = correo

        # 5) Enviar por SMTP
        try:
            servidor = smtplib.SMTP(
                current_app.config['SMTP_SERVER'],
                current_app.config['SMTP_PORT']
            )
            servidor.starttls()
            servidor.login(
                current_app.config['SMTP_USER'],
                current_app.config['SMTP_PASS']
            )
            servidor.send_message(msg)
            servidor.quit()
            flash('¡Tu mensaje ha sido enviado con éxito!', 'success')
        except Exception as e:
            current_app.logger.error(f'Error enviando correo: {e}')
            flash('Ocurrió un error al enviar tu mensaje. Intenta más tarde.', 'danger')

        return redirect(url_for('contacto'))

    # GET: mostrar el formulario
    return render_template('contacto.html')
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
