from app import create_app, db
from app.models import Role, User, Genre

app = create_app()
with app.app_context():
    # очистка
    db.session.query(Role).delete()
    db.session.query(User).delete()
    db.session.query(Genre).delete()
    db.session.commit()

    # роли
    for id, name in [(1,'администратор'),(2,'модератор'),(3,'пользователь')]:
        db.session.add(Role(id=id, name=name, description=''))
    db.session.commit()
    print("Роли добавлены")

    # жанры
    for name in ['Фантастика','Детектив','Роман','Научная литература','История','Приключения','Поэма','Комедия']:
        db.session.add(Genre(name=name))
    db.session.commit()
    print("Жанры добавлены")

    # пользователи
    for login, pwd, first, last, role_id in [
        ('admin','admin123','Админ','Администраторов',1),
        ('moderator','moderator123','Модер','Модераторов',2),
        ('user','user123','Пользователь','Обычный',3)
    ]:
        u = User(login=login, first_name=first, last_name=last, role_id=role_id)
        u.set_password(pwd)
        db.session.add(u)
    db.session.commit()
    print("Пользователи добавлены")