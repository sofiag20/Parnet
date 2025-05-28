from models.Database import db

class Producto(db.Model):
    __tablename__ = 'producto'  # Coincide con la tabla real

    id_producto = db.Column(db.Integer, primary_key=True)  # Coincide con el nombre real
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Enum('existencia', 'agotado'), default='existencia')
    imagen = db.Column(db.String(255), nullable=True)

