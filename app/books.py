from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, session, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
import uuid

from app.models import db
from app.repositories import BookRepository, UserRepository, GenreRepository, ImageRepository, ReviewRepository, ViewRepository

user_repository = UserRepository(db)
book_repository = BookRepository(db)
genre_repository = GenreRepository(db)
image_repository = ImageRepository(db)
review_repository = ReviewRepository(db)
view_repository = ViewRepository(db)

bp = Blueprint('books', __name__, url_prefix='/books')

def search_params():
    return {
        'name': request.args.get('name'),
        'genre_ids': [int(x) for x in request.args.getlist('genre_ids') if x],
    }

def can_edit_book(book):
    return current_user.is_authenticated and (current_user.is_admin() or current_user.is_moderator())

def can_delete_book(book):
    return current_user.is_authenticated and current_user.is_admin()

@bp.route('/')
def index():
    # Получение списка книг с пагинацией и фильтрацией
    pagination = book_repository.get_pagination_info(**search_params())
    books = book_repository.get_all_books(pagination=pagination)
    genres = genre_repository.get_all_genres()

    # Для варианта 4
    popular_books = view_repository.get_popular_books(limit=5, months=3)
    if current_user.is_authenticated:
        recent_books = view_repository.get_recent_views(user_id=current_user.id, limit=5)
    else:
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        recent_books = view_repository.get_recent_views(session_id=session_id, limit=5)

    return render_template('books/index.html',
                           books=books,
                           genres=genres,
                           pagination=pagination,
                           search_params=search_params(),
                           popular_books=popular_books,
                           recent_books=recent_books)

@bp.route('/new')
@login_required
def new():
    if not current_user.is_admin():
        flash('У вас недостаточно прав для добавления книги.', 'danger')
        return redirect(url_for('books.index'))
    book = book_repository.new_book()
    genres = genre_repository.get_all_genres()
    return render_template('books/new.html', genres=genres, book=book)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    if not current_user.is_admin():
        flash('У вас недостаточно прав для добавления книги.', 'danger')
        return redirect(url_for('books.index'))
    f = request.files.get('cover_image')
    img = None
    book = None

    try:
        if f and f.filename:
            img = image_repository.add_image(f)
        image_id = img.id if img else None
        genre_ids = request.form.getlist('genre_ids')
        if genre_ids:
            genre_ids = [int(g) for g in genre_ids]
        book = book_repository.add_book(
            name=request.form['name'],
            short_desc=request.form['short_desc'],
            full_desc=request.form['full_desc'],
            year=request.form.get('year') or None,
            publisher=request.form.get('publisher'),
            pages=request.form.get('pages') or None,
            author_name=request.form['author_name'],
            cover_image_id=image_id,
            genre_ids=genre_ids
        )
    except IntegrityError as err:
        flash(f'Ошибка при сохранении книги. Проверьте данные. ({err})', 'danger')
        genres = genre_repository.get_all_genres()
        return render_template('books/new.html', genres=genres, book=book)

    flash(f'Книга "{book.name}" успешно добавлена!', 'success')
    return redirect(url_for('books.index'))

@bp.route('/<int:book_id>')
def show(book_id):
    book = book_repository.get_book_by_id(book_id)
    if book is None:
        abort(404)

    # Учёт просмотра (вариант 4)
    user_id = current_user.id if current_user.is_authenticated else None
    session_id = None
    if not user_id:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        session_id = session['session_id']
    view_repository.add_view(book_id, user_id, session_id)

    recent_reviews = review_repository.get_by_book_id(book_id, limit=5, sort_by='newest')
    user_review = None
    if current_user.is_authenticated:
        user_review = review_repository.get_user_review_for_book(book_id, current_user.id)

    return render_template('books/show.html',
                           book=book,
                           reviews=recent_reviews,
                           user_review=user_review)

@bp.route('/<int:book_id>/reviews')
def reviews(book_id):
    book = book_repository.get_book_by_id(book_id)
    if book is None:
        abort(404)

    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'newest')
    per_page = 10

    pagination = review_repository.get_pagination(book_id, page, per_page, sort_by)
    all_reviews = pagination.items

    user_review = None
    if current_user.is_authenticated:
        user_review = review_repository.get_user_review_for_book(book_id, current_user.id)

    return render_template('books/reviews.html',
                           book=book,
                           reviews=all_reviews,
                           pagination=pagination,
                           sort_by=sort_by,
                           user_review=user_review)

@bp.route('/<int:book_id>/review/create', methods=['POST'])
@login_required
def create_review(book_id):
    book = book_repository.get_book_by_id(book_id)
    if book is None:
        abort(404)

    existing_review = review_repository.get_user_review_for_book(book_id, current_user.id)
    if existing_review:
        flash('Вы уже оставили отзыв на эту книгу.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))

    rating = request.form.get('rating', type=int)
    text = request.form.get('text', '').strip()

    if rating is None or rating < 0 or rating > 5:
        flash('Некорректная оценка.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))
    if not text:
        flash('Текст отзыва не может быть пустым.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))

    review_repository.add_review(book_id, current_user.id, rating, text)

    # Пересчитать рейтинг
    all_reviews = review_repository.get_by_book_id(book_id)
    total_rating = sum(r.rating for r in all_reviews)
    total_count = len(all_reviews)
    book.rating_sum = total_rating
    book.rating_num = total_count
    db.session.commit()

    flash('Ваш отзыв успешно добавлен!', 'success')
    return redirect(url_for('books.show', book_id=book_id))

@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    book = book_repository.get_book_by_id(book_id)
    if not book:
        abort(404)
    if not can_edit_book(book):
        flash('У вас нет прав для редактирования этой книги.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))

    genres = genre_repository.get_all_genres()

    if request.method == 'POST':
        genre_ids = request.form.getlist('genre_ids')
        if genre_ids:
            genre_ids = [int(g) for g in genre_ids]
        try:
            book_repository.update_book(
                book_id=book_id,
                name=request.form['name'],
                short_desc=request.form['short_desc'],
                full_desc=request.form['full_desc'],
                year=request.form.get('year') or None,
                publisher=request.form.get('publisher'),
                pages=request.form.get('pages') or None,
                author_name=request.form['author_name'],
                genre_ids=genre_ids
            )
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('books.show', book_id=book_id))
        except Exception as e:
            flash(f'Ошибка при сохранении: {e}', 'danger')
            return render_template('books/edit.html', book=book, genres=genres)

    return render_template('books/edit.html', book=book, genres=genres)

@bp.route('/<int:book_id>/delete', methods=['POST'])
@login_required
def delete(book_id):
    book = book_repository.get_book_by_id(book_id)
    if not book:
        abort(404)
    if not can_delete_book(book):
        flash('У вас нет прав для удаления этой книги.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))
    book_repository.delete_book(book_id)
    flash(f'Книга "{book.name}" удалена.', 'success')
    return redirect(url_for('books.index'))

@bp.route('/images/<image_id>')
def image(image_id):
    img = image_repository.get_by_id(image_id)
    if img is None:
        abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], img.storage_filename)