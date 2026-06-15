from flask_sqlalchemy import SQLAlchemy
from app.models import Book, Genre
from app.repositories.base_repository import BaseRepository

class BookRepository(BaseRepository):
    model = Book

    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_all_books(self, pagination=None):
        query = self.db.session.query(Book).order_by(Book.year.desc())
        if pagination:
            return query.paginate(page=pagination.page, per_page=pagination.per_page, error_out=False)
        return query.all()

    def get_book_by_id(self, book_id):
        return self.db.session.query(Book).filter_by(id=book_id).first()

    def add_book(self, name, short_desc, full_desc, year, publisher, pages, author_name, cover_image_id=None, genre_ids=None):
        book = Book(
            name=name,
            short_desc=short_desc,
            full_desc=full_desc,
            year=year,
            publisher=publisher,
            pages=pages,
            author_name=author_name,
            cover_image_id=cover_image_id
        )
        self.db.session.add(book)
        self.db.session.flush()
        if genre_ids:
            genres = self.db.session.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            book.genres = genres
        self.db.session.commit()
        return book

    def update_book(self, book_id, name, short_desc, full_desc, year, publisher, pages, author_name, genre_ids=None):
        book = self.get_book_by_id(book_id)
        if not book:
            return None
        book.name = name
        book.short_desc = short_desc
        book.full_desc = full_desc
        book.year = year
        book.publisher = publisher
        book.pages = pages
        book.author_name = author_name
        if genre_ids is not None:
            genres = self.db.session.query(Genre).filter(Genre.id.in_(genre_ids)).all()
            book.genres = genres
        self.db.session.commit()
        return book

    def delete_book(self, book_id):
        book = self.get_book_by_id(book_id)
        if book:
            self.db.session.delete(book)
            self.db.session.commit()
            return True
        return False

    def get_pagination_info(self, page=1, per_page=10, name=None, genre_ids=None):
        query = self.db.session.query(Book)
        if name:
            query = query.filter(Book.name.ilike(f'%{name}%'))
        if genre_ids:
            query = query.join(Book.genres).filter(Genre.id.in_(genre_ids)).distinct()
        pagination = query.order_by(Book.year.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pagination

    def new_book(self):
        return Book()