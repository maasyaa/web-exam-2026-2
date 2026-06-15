from flask_sqlalchemy import SQLAlchemy
from app.models import User, Role
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    model = User

    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_user_by_login(self, login):
        return self.db.session.query(User).filter_by(login=login).first()

    def get_user_by_id(self, user_id):
        return self.db.session.query(User).filter_by(id=user_id).first()

    def get_all_users(self):
        return self.db.session.query(User).all()

    def create_user(self, login, password, first_name, last_name, middle_name=None, role_id=3):
        user = User(
            login=login,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role_id=role_id
        )
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def get_role_by_name(self, name):
        return self.db.session.query(Role).filter_by(name=name).first()