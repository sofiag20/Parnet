from flask import Flask, render_template
from models.Database import Database
from models.Noticia import Noticia

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Aquí sí se inicializa la app con Singleton correctamente
db = Database.get_instance(app)

@app.route("/")
def index():
    noticias = Noticia.query.order_by(Noticia.id_notice.desc()).limit(5).all()
    return render_template("index.html", noticias=noticias)



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

if __name__ == "__main__":
    app.run()



