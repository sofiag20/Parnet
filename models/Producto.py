from App import db

class Producto(db.Model):
    __tablename__ = 'producto' 

    id_producto = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(255))  # Ruta de la imagen o nombre de archivo
