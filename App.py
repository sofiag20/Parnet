import smtplib   
import os
from flask_paginate import Pagination, get_page_parameter
from io import BytesIO
import requests
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import pandas as pd
import logging
from reportlab.lib.utils import ImageReader
from collections import Counter
import matplotlib.pyplot as plt
from sqlalchemy import func
from datetime import date


from flask import (
    Flask, render_template, redirect, url_for,
    session, request, current_app, flash,send_file, abort,jsonify,Response
)
from flask_socketio import SocketIO, emit
from models.Database import Database
from models.Noticia   import Noticia
from models.Visita    import Visita
from models.Usuario   import Usuario
from models.Producto  import Producto
from models.Contacto import ContactoForm
from email.mime.text import MIMEText
from models.Sugerencia import Sugerencia,SugerenciaForm
from models.Servicio import Servicio
from forms.solicitud_servicio import ServicioForm
from models.Area import Area

# Instancia única de SQLAlchemy
db = Database.get_instance()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.logger.setLevel(logging.DEBUG)
app.secret_key = "admin123"
app.config['SQLALCHEMY_DATABASE_URI']        = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = '4338b5a9e5c318f36ecc450a84236f2edb254dea3a2ee6ff'
app.config['RECAPTCHA_PUBLIC_KEY']  = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'


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

@app.route("/contenido/socios")
def contenido_socios():
    return render_template("fragmentos/socios.html")

@app.route("/contenido/casos_exito")
def contenido_casos_exito():
    return render_template("fragmentos/casos_exito.html")


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

@app.route('/contenido/contacto', methods=['GET','POST'])
def contenido_contacto():
    form = ContactoForm()
    if form.validate_on_submit():
        # envío de correo…
        flash('¡Tu mensaje ha sido enviado con éxito!', 'success')
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

@app.route('/contenido/login2')
def contenido_login2():
    return render_template('fragmentos/login2.html')

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

@app.route('/contenido/productos_admin2')
def contenido_productos_admin2():
    if session.get("rol") != "admin":
        return redirect(url_for("login2"))
    productos = Producto.query.all()
    return render_template('fragmentos/productos_admin2.html', productos=productos)

@app.route('/contenido/producto')
def contenido_productos():
    q = request.args.get('q', '').strip()
    if q:
        productos = Producto.query.filter(Producto.descripcion.ilike(f'%{q}%')).all()
    else:
        productos = Producto.query.all()
    return render_template('fragmentos/producto.html', productos=productos)

@app.route('/contenido/producto/<int:id>')
def contenido_producto_detalle(id):
    producto = Producto.query.get_or_404(id)
    return render_template('fragmentos/producto_detalle.html',producto=producto)

@app.route('/producto/<int:id>/exportar')
def export_producto_pdf(id):
    producto = Producto.query.get_or_404(id)

    # Preparamos canvas
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, h - 50, f"Ficha Técnica – {producto.descripcion}")

    # Punto de inicio del texto
    y_start = h - 100

    # Intento de carga de imagen
    try:
        img_field = (producto.imagen or "").strip()
        img = None

        if img_field.lower().startswith(('http://','https://')):
            resp = requests.get(img_field, timeout=5)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content))
        else:
            # asumimos ruta local en /static
            ruta_rel = img_field.lstrip('/')
            path = os.path.join(current_app.root_path, ruta_rel)
            if os.path.exists(path):
                img = Image.open(path)

        if img:
            # redimensionar a 150px de alto
            max_h = 150
            ratio = max_h / float(img.height)
            img_w, img_h = int(img.width * ratio), int(max_h)

            # remuestreo con Lanczos
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img_resized = img.resize((img_w, img_h), resample)

            # ponemos la imagen en un ImageReader
            buf2 = BytesIO()
            img_resized.save(buf2, format='PNG')
            buf2.seek(0)
            img_reader = ImageReader(buf2)    # <-- aquí

            # dibujamos usando el ImageReader
            p.drawImage(
                img_reader,
                40, h - 80 - img_h,
                width=img_w,
                height=img_h,
                mask='auto'
            )

            y_start = h - 80 - img_h - 20

    except Exception as e:
        current_app.logger.warning(f"[PDF] Error cargando imagen: {e}")

    # Datos debajo de la imagen (o más arriba si no hay)
    p.setFont("Helvetica", 12)
    y = y_start
    p.drawString(40, y, f"ID: {producto.id_producto}")
    y -= 20
    p.drawString(40, y, f"Descripción: {producto.descripcion}")
    y -= 20
    p.drawString(40, y, f"Precio: ${producto.costo:.2f}")
    y -= 20
    p.drawString(40, y, f"Estatus: {producto.stock.capitalize()}")

    # Finalizar PDF
    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        download_name=f"producto_{producto.id_producto}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )

@app.route('/admin/productos/reporte')
def reporte_productos_pdf():
    # 1) Consulta todos los productos
    productos = Producto.query.order_by(Producto.id_producto).all()

    # 2) Prepara canvas
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # 3) Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 50, "Reporte de Productos")

    # 4) Cabeceras de tabla
    y = height - 80
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "ID")
    p.drawString(100, y, "Descripción")
    p.drawString(350, y, "Costo")
    p.drawString(430, y, "Estatus")

    # 5) Filas
    p.setFont("Helvetica", 11)
    y -= 20
    for prod in productos:
        if y < 40:
            p.showPage()
            y = height - 50
        p.drawString(40, y, str(prod.id_producto))
        p.drawString(100, y, prod.descripcion[:30])  # recortamos a 30 chars
        p.drawString(350, y, f"${prod.costo:.2f}")
        p.drawString(430, y, prod.stock.capitalize())
        y -= 18

    # 6) Finaliza
    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        download_name="reporte_productos.pdf",
        as_attachment=True,
        mimetype="application/pdf"
    )


@app.route('/admin/productos/export_excel')
def reporte_productos_excel():
    # 1) Consulta todos los productos
    productos = Producto.query.order_by(Producto.id_producto).all()

    # 2) Construye un DataFrame
    datos = []
    for p in productos:
        datos.append({
            'ID': p.id_producto,
            'Descripción': p.descripcion,
            'Costo': float(p.costo),
            'Stock': 'En existencia' if p.stock == 'existencia' else 'Agotado'
        })
    df = pd.DataFrame(datos)

    # 3) Escribe en un buffer en memoria
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer,
                    index=False,
                    sheet_name='Productos')
    buffer.seek(0)

    # 4) Envíalo como descarga
    return send_file(
        buffer,
        as_attachment=True,
        download_name='reporte_productos.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/contenido/sugerencias', methods=['GET','POST'])
def contenido_sugerencias():
    form = SugerenciaForm()
    if form.validate_on_submit():
        # Guardar en BD...
        nueva = Sugerencia(
            nombre  = form.nombre.data,
            mensaje = form.mensaje.data
        )
        db.session.add(nueva)
        db.session.commit()
        flash('¡Gracias por tu sugerencia!', 'success')
        # Re–renderiza el mismo fragmento para mostrar el flash
    return render_template('fragmentos/sugerencias.html', form=form)

@app.route('/contenido/sugerencias_admin')
def contenido_sugerencias_admin():
    if session.get('rol') != 'admin':
        return redirect(url_for('login2'))

    # Lee ?page= de la URL, por defecto 1
    page     = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    # Consulta paginada
    query       = Sugerencia.query.order_by(Sugerencia.creado_el.desc())
    total       = query.count()
    sugerencias = query.offset((page-1)*per_page).limit(per_page).all()

    # Construye el paginador
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='bootstrap5',
        href=url_for('contenido_sugerencias_admin') + '?page={0}'
    )

    # Renderiza tu fragmento, pasando SÍ o SÍ both variables
    return render_template(
        'fragmentos/admin_sugerencias.html',
        sugerencias=sugerencias,
        pagination=pagination
    )

# 1) Listado paginado de sugerencias
@app.route('/admin/sugerencias')
def listar_sugerencias():
    # Restringir a admin
    if session.get('rol') != 'admin':
        return redirect(url_for('login2'))

    # Parámetros de paginación
    page     = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    # Consulta base
    query       = Sugerencia.query.order_by(Sugerencia.creado_el.desc())
    total       = query.count()
    sugerencias = query.offset((page - 1) * per_page).limit(per_page).all()

    # Paginador para el template
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=total,
                            css_framework='bootstrap5')

    return render_template('admin_sugerencias.html',
                        sugerencias=sugerencias,
                        pagination=pagination)



@app.route('/admin/sugerencias/export')
def export_sugerencias():
    # Restringir a admin
    if session.get('rol') != 'admin':
        return redirect(url_for('login2'))

    fmt = request.args.get('fmt', 'excel').lower()
    all_sug = Sugerencia.query.order_by(Sugerencia.creado_el.desc()).all()

    # === Excel ===
    if fmt == 'excel':
        # Prepara lista de dicts
        data = [{
            'ID':      s.id,
            'Nombre':  s.nombre,
            'Mensaje': s.mensaje,
            'Fecha':   s.creado_el.strftime('%Y-%m-%d %H:%M')
        } for s in all_sug]

        # Crea DataFrame
        df = pd.DataFrame(data)

        # Escribe a Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sugerencias')
            ws = writer.sheets['Sugerencias']
            # Ajusta anchos de columna
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                ws.set_column(idx, idx, max_len)
        output.seek(0)

        return send_file(
            output,
            download_name='sugerencias.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # === PDF via ReportLab ===
    elif fmt == 'pdf':
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Título
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, height - 40, "Listado de Sugerencias")

        # Encabezados
        y = height - 80
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y, "ID")
        p.drawString(80, y, "Nombre")
        p.drawString(220, y, "Mensaje")
        p.drawString(500, y, "Fecha")

        # Filas
        p.setFont("Helvetica", 9)
        y -= 20
        for s in all_sug:
            if y < 40:
                p.showPage()
                y = height - 40
            p.drawString(40, y, str(s.id))
            p.drawString(80, y, s.nombre[:20])
            msg = (s.mensaje[:30] + '...') if len(s.mensaje) > 30 else s.mensaje
            p.drawString(220, y, msg)
            p.drawString(500, y, s.creado_el.strftime('%Y-%m-%d'))
            y -= 15

        p.save()
        buffer.seek(0)

        return send_file(
            buffer,
            download_name='sugerencias.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )

    # Formato no soportado
    else:
        return "Formato no soportado", 400

@app.route('/contenido/servicios/solicitud', methods=['GET', 'POST'])
def contenido_solicitud_servicio():
    form = ServicioForm()
    form.area.choices = [(a.id_area, a.des_area) for a in Area.query.order_by(Area.des_area).all()]

    if form.validate_on_submit():
        nueva = Servicio(
            fecha   = date.today(),
            detalle = form.detalle.data,
            id_area = form.area.data
        )
        db.session.add(nueva)
        db.session.commit()
        flash('¡Tu solicitud se ha enviado con éxito!', 'success')
        return redirect(url_for('contenido_solicitud_servicio'))

    return render_template('fragmentos/solicitud_servicio.html', form=form)

# ——————————————————————————————
# EJECUCIÓN
# ——————————————————————————————

if __name__ == "__main__":
    # Arranca HTTP + WebSocket
    socketio.run
