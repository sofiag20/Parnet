from App import db

class Servicio(db.Model):
    __tablename__ = 'servicio'

    id_servicio = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    detalle = db.Column(db.Text, nullable=False)

    id_area = db.Column(db.Integer, db.ForeignKey('area.id_area'), nullable=True)
    area = db.relationship('Area', backref='servicios')
