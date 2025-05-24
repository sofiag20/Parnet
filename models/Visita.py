from models.Database import Database

db = Database.get_instance()

class Visita(db.Model):
    __tablename__ = 'visitas'

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer, default=0)

    def __init__(self, total=0):
        self.total = total
