from flask import Blueprint, render_template, request, abort, Response
from flask_login import login_required, current_user
from io import StringIO
import csv
from datetime import datetime

from app.models import db
from app.repositories import ViewRepository, BookRepository, UserRepository

view_repository = ViewRepository(db)
book_repository = BookRepository(db)
user_repository = UserRepository(db)

bp = Blueprint('statistics', __name__, url_prefix='/statistics')

def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)

@bp.route('/')
@login_required
def index():
    admin_required()
    return render_template('statistics/index.html')


@bp.route('/user-actions')
@login_required
def user_actions():
    admin_required()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = view_repository.get_user_actions_paginated(page, per_page)

    actions = []
    for view in pagination.items:
        book = book_repository.get_book_by_id(view.book_id)
        user = user_repository.get_user_by_id(view.user_id) if view.user_id else None
        actions.append({
            'id': view.id,
            'book_name': book.name if book else 'Удалённая книга',
            'user_fullname': user.full_name if user else 'Неаутентифицированный пользователь',
            'viewed_at': view.viewed_at
        })
    pagination.items = actions
    return render_template('statistics/user_actions.html', pagination=pagination)

@bp.route('/user-actions/export')
@login_required
def export_user_actions():
    admin_required()
    all_views = view_repository.get_all_user_actions()
    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['№', 'ФИО пользователя', 'Название книги', 'Дата и время просмотра'])

    for idx, view in enumerate(all_views, start=1):
        book = book_repository.get_book_by_id(view.book_id)
        user = user_repository.get_user_by_id(view.user_id) if view.user_id else None
        writer.writerow([
            idx,
            user.full_name if user else 'Неаутентифицированный пользователь',
            book.name if book else 'Удалённая книга',
            view.viewed_at.strftime('%d.%m.%Y %H:%M:%S')
        ])

    filename = f'user_actions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@bp.route('/book-stats')
@login_required
def book_stats():
    admin_required()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    pagination = view_repository.get_book_stats_paginated(page, per_page, date_from, date_to)

    stats = []
    for book, view_count in pagination.items:
        stats.append({
            'id': book.id,
            'name': book.name,
            'view_count': view_count
        })
    pagination.items = stats
    return render_template('statistics/book_stats.html', pagination=pagination, date_from=date_from, date_to=date_to)

@bp.route('/book-stats/export')
@login_required
def export_book_stats():
    admin_required()
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    all_stats = view_repository.get_all_book_stats(date_from, date_to)

    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['№', 'Название книги', 'Количество просмотров'])

    for idx, (book, view_count) in enumerate(all_stats, start=1):
        writer.writerow([idx, book.name, view_count])

    filename = f'book_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )