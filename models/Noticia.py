from App import db

class Noticia(db.Model):
    __tablename__ = 'noticias'

    id_notice = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    nota = db.Column(db.Text, nullable=False)
