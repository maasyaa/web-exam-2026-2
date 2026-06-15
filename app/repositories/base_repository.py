from flask_sqlalchemy import SQLAlchemy

class BaseRepository:
    model = None

    def __init__(self, db: SQLAlchemy):
        self.db = db