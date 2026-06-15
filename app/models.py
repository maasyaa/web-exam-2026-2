import os
from typing import Optional, List
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, MetaData, Table, Column


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

# связующая таблица книга-жанр
book_genre = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)


class Genre(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    books: Mapped[List["Book"]] = relationship(secondary=book_genre, back_populates="genres")


class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class User(Base, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, default=3)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    role: Mapped["Role"] = relationship()
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    views: Mapped[List["PageView"]] = relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def is_admin(self):
        return self.role and self.role.name == 'администратор'

    def is_moderator(self):
        return self.role and self.role.name == 'модератор'


class Image(Base):
    __tablename__ = 'images'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    object_id: Mapped[Optional[int]]
    object_type: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('books.image', image_id=self.id)


class Book(Base):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_desc: Mapped[str] = mapped_column(Text, nullable=False)
    full_desc: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    publisher: Mapped[Optional[str]] = mapped_column(String(200))
    pages: Mapped[Optional[int]] = mapped_column(Integer)
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rating_sum: Mapped[int] = mapped_column(default=0)
    rating_num: Mapped[int] = mapped_column(default=0)
    cover_image_id: Mapped[Optional[str]] = mapped_column(ForeignKey("images.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    cover_image: Mapped[Optional["Image"]] = relationship()
    reviews: Mapped[List["Review"]] = relationship(back_populates="book", cascade="all, delete-orphan")
    views: Mapped[List["PageView"]] = relationship(back_populates="book")
    genres: Mapped[List["Genre"]] = relationship(secondary=book_genre, back_populates="books")

    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum / self.rating_num
        return 0


class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book: Mapped["Book"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class PageView(Base):
    __tablename__ = 'page_views'
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    viewed_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    book: Mapped["Book"] = relationship(back_populates="views")
    user: Mapped["User"] = relationship(back_populates="views")