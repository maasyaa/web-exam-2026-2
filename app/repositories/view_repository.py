from datetime import datetime, timedelta
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from app.models import PageView, Book
from app.repositories.base_repository import BaseRepository

class ViewRepository(BaseRepository):
    model = PageView

    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def add_view(self, book_id: int, user_id: int = None, session_id: str = None):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = self.db.session.query(PageView).filter(
            PageView.book_id == book_id,
            PageView.viewed_at >= today_start
        )
        if user_id:
            query = query.filter(PageView.user_id == user_id)
        elif session_id:
            query = query.filter(PageView.session_id == session_id)
        else:
            return None
        if query.count() >= 10:
            return None
        view = PageView(book_id=book_id, user_id=user_id, session_id=session_id)
        self.db.session.add(view)
        self.db.session.commit()
        return view

    def get_popular_books(self, limit: int = 5, months: int = 3):
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        popular = (
            self.db.session.query(
                Book,
                func.count(PageView.id).label('view_count')
            )
            .join(PageView, PageView.book_id == Book.id)
            .filter(PageView.viewed_at >= cutoff_date)
            .group_by(Book.id)
            .order_by(func.count(PageView.id).desc())
            .limit(limit)
            .all()
        )
        return [book for book, _ in popular]

    def get_recent_views(self, user_id: int = None, session_id: str = None, limit: int = 5):
        if not user_id and not session_id:
            return []
        query = self.db.session.query(Book).join(PageView, PageView.book_id == Book.id)
        if user_id:
            query = query.filter(PageView.user_id == user_id)
        else:
            query = query.filter(PageView.session_id == session_id)
        query = query.order_by(PageView.viewed_at.desc()).limit(limit)
        return query.all()

    def get_user_actions_paginated(self, page: int, per_page: int = 10):
        query = self.db.session.query(PageView).order_by(PageView.viewed_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_all_user_actions(self):
        return self.db.session.query(PageView).order_by(PageView.viewed_at.desc()).all()

    def get_book_stats_paginated(self, page: int, per_page: int = 10, date_from: str = None, date_to: str = None):
        query = (
            self.db.session.query(
                Book,
                func.count(PageView.id).label('view_count')
            )
            .join(PageView, PageView.book_id == Book.id)
            .filter(PageView.user_id.isnot(None))
        )
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(PageView.viewed_at >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PageView.viewed_at < date_to_obj)
            except ValueError:
                pass
        query = query.group_by(Book.id).order_by(func.count(PageView.id).desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_all_book_stats(self, date_from: str = None, date_to: str = None):
        query = (
            self.db.session.query(
                Book,
                func.count(PageView.id).label('view_count')
            )
            .join(PageView, PageView.book_id == Book.id)
            .filter(PageView.user_id.isnot(None))
        )
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(PageView.viewed_at >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PageView.viewed_at < date_to_obj)
            except ValueError:
                pass
        query = query.group_by(Book.id).order_by(func.count(PageView.id).desc())
        return query.all()