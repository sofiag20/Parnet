from flask_sqlalchemy import SQLAlchemy

class Database:
    _instance = None

    @staticmethod
    def get_instance():
        if Database._instance is None:
            Database._instance = SQLAlchemy()
            print("🔄 SQLAlchemy (Singleton) instanciado")
        return Database._instance
