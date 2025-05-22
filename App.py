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

if __name__ == "__main__":
    app.run()
    


