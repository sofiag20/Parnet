from models.Database import db

class Area(db.Model):
    __tablename__ = 'area'

    id_area = db.Column(db.Integer, primary_key=True)
    des_area = db.Column(db.String(100), nullable=False)
