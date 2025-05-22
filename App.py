from flask import Flask,render_template
from models.Database import Database # Importa el Singleton

app = Flask(__name__)

# Configura la conexión a tu base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/parnet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Obtén la instancia única de SQLAlchemy y asóciala a la app Flask
db = Database.get_instance()
db.init_app(app)


@app.route("/")
def index():
    return render_template('index.html')

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
    


