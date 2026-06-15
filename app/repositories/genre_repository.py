from flask_sqlalchemy import SQLAlchemy
from app.models import Genre
from app.repositories.base_repository import BaseRepository

class GenreRepository(BaseRepository):
    model = Genre

    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_all_genres(self):
        return self.db.session.query(Genre).order_by(Genre.name).all()

    def get_genre_by_id(self, genre_id):
        return self.db.session.query(Genre).filter_by(id=genre_id).first()

    def get_genres_by_ids(self, ids):
        return self.db.session.query(Genre).filter(Genre.id.in_(ids)).all()