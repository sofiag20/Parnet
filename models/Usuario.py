from App import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), unique=True, nullable=False)
    pw = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'publico'), default='publico')
