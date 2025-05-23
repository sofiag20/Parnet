# models/Database.py
from flask_sqlalchemy import SQLAlchemy

class Database:
    _instance = None

    @staticmethod
    def get_instance(app=None):
        if Database._instance is None:
            Database._instance = SQLAlchemy()
            print("🔄 SQLAlchemy (Singleton) instanciado")
        
        # solo llamar init_app si se proporciona la app y aún no fue inicializado
        if app is not None:
            Database._instance.init_app(app)
        
        return Database._instance

