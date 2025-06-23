import os
from flask import Flask
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash

from config import Config
from extentions import db, login_manager
from models import Role, Animal, User, AdoptionRequest, Photo

csrf = CSRFProtect()
def add_sample_animals():
    sample_animals = [
        {"name": "Барсик", "description": "Добрый котик", "age": 3, "breed": "Мейн-кун", "gender": "мужской"},
        {"name": "Мурка", "description": "Ласковая кошка", "age": 2, "breed": "Сиамская", "gender": "женский"},
        {"name": "Рекс", "description": "Верный пес", "age": 5, "breed": "Лабрадор", "gender": "мужской"},
        {"name": "Белка", "description": "Активная белочка", "age": 1, "breed": "Белка", "gender": "женский"},
        {"name": "Том", "description": "Любит играть", "age": 4, "breed": "Дворовый", "gender": "мужской"},
        {"name": "Джессика", "description": "Нежная и добрая", "age": 3, "breed": "Британская", "gender": "женский"},
        {"name": "Бобик", "description": "Большой и сильный", "age": 6, "breed": "Овчарка", "gender": "мужской"},
        {"name": "Пушок", "description": "Очень пушистый кот", "age": 2, "breed": "Персидская", "gender": "мужской"},
        {"name": "Люси", "description": "Весёлая и игривая", "age": 1, "breed": "Такса", "gender": "женский"},
        {"name": "Макс", "description": "Отважный и сильный", "age": 4, "breed": "Хаски", "gender": "мужской"},
        {"name": "Барсик1", "description": "Добрый котик", "age": 3, "breed": "Мейн-кун", "gender": "мужской"},
        {"name": "Мурка1", "description": "Ласковая кошка", "age": 2, "breed": "Сиамская", "gender": "женский"},
        {"name": "Рекс1", "description": "Верный пес", "age": 5, "breed": "Лабрадор", "gender": "мужской"},
        {"name": "Белка1", "description": "Активная белочка", "age": 1, "breed": "Белка", "gender": "женский"},
        {"name": "Том1", "description": "Любит играть", "age": 4, "breed": "Дворовый", "gender": "мужской"},
        {"name": "Джессика1", "description": "Нежная и добрая", "age": 3, "breed": "Британская", "gender": "женский"},
        {"name": "Бобик1", "description": "Большой и сильный", "age": 6, "breed": "Овчарка", "gender": "мужской"},
        {"name": "Пушок1", "description": "Очень пушистый кот", "age": 2, "breed": "Персидская", "gender": "мужской"},
        {"name": "Люси1", "description": "Весёлая и игривая", "age": 1, "breed": "Такса", "gender": "женский"},
        {"name": "Макс1", "description": "Отважный и сильный", "age": 4, "breed": "Хаски", "gender": "мужской"}
    ]

    for a in sample_animals:
        animal = Animal(
            name=a["name"],
            description=a["description"],
            age=a["age"],
            breed=a["breed"],
            gender=a["gender"],
            status="available"
        )
        db.session.add(animal)
    db.session.commit()

def create_roles_and_admins():
    from models import Role, User
    from __init__ import db

    admin_role = Role.query.filter_by(name='administrator').first()
    if not admin_role:
        admin_role = Role(name='administrator', description='Администратор')
        db.session.add(admin_role)

    moderator_role = Role.query.filter_by(name='moderator').first()
    if not moderator_role:
        moderator_role = Role(name='moderator', description='Модератор')
        db.session.add(moderator_role)

    admin_user = User.query.filter_by(login='admin').first()
    if not admin_user:
        admin_user = User(
            login='admin',
            last_name='Админ',
            first_name='Главный',
            middle_name='',
            role=admin_role
        )
        admin_user.set_password('password')
        db.session.add(admin_user)

    mod_user = User.query.filter_by(login='moderator').first()
    if not mod_user:
        mod_user = User(
            login='moderator',
            last_name='Модератор',
            first_name='Средний',
            middle_name='',
            role=moderator_role
        )
        mod_user.set_password('password')
        db.session.add(mod_user)

    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    login_manager.init_app(app)

    # with app.app_context():
    #     # create_roles_and_admins()
    #     # users = User.query.all()
    #     # print("Список пользователей в базе:")
    #     # for u in users:
    #     #     role_name = u.role.name if u.role else "Нет роли"
    #     #     print(f"ID: {u.id}, Логин: {u.login}, Имя: {u.first_name} {u.last_name}, Роль: {role_name}, Пароль: {u.password_hash}")
    #     # add_sample_animals()
    #     add_sample_animals()
    #     create_roles_and_admins()

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes import routes
    app.register_blueprint(routes)

    return app