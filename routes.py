from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, send_from_directory
)
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import markdown
import bleach

from extentions import db
from models import Animal, Photo, AdoptionRequest, User, Role
from forms import AnimalForm, LoginForm, AdoptionForm, RegistrationForm
from utils import allowed_file, save_images, sanitize_markdown

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    animals = Animal.query.order_by(
        Animal.status.desc(), Animal.id.desc()
    ).paginate(page=page, per_page=10)
    return render_template('index.html', animals=animals)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = User.query.all()
        print(users)
        for u in users:
            print(u.login)
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Успешный вход.', 'success')
            return redirect(request.args.get('next') or url_for('routes.index'))
        print(form.login.data)
        print(user.check_password(form.password.data))
        flash('Невозможно аутентифицироваться с указанными логином и паролем.', 'danger')
    return render_template('login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(request.referrer or url_for('routes.index'))

@routes.route('/animal/add', methods=['GET', 'POST'])
@login_required
def animal_add():
    if not current_user.is_admin():
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('routes.index'))

    form = AnimalForm()
    if form.validate_on_submit():
        try:
            new_animal = Animal(
                name=form.name.data,
                description=sanitize_markdown(form.description.data),
                age=form.age.data,
                breed=form.breed.data,
                gender=form.gender.data,
                status='available'
            )
            db.session.add(new_animal)
            db.session.flush()

            save_images(request.files.getlist('images'), new_animal.id)

            db.session.commit()
            flash('Животное успешно добавлено.', 'success')
            return redirect(url_for('routes.animal_detail', animal_id=new_animal.id, form=form))
        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка.', 'danger')
    return render_template('animal_form.html', form=form, action="Добавить")

@routes.route('/animal/<int:animal_id>/edit', methods=['GET', 'POST'])
@login_required
def animal_edit(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if not current_user.can_edit():
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('routes.index'))

    form = AnimalForm(obj=animal)
    if form.validate_on_submit():
        try:
            animal.name = form.name.data
            animal.description = sanitize_markdown(form.description.data)
            animal.age = form.age.data
            animal.breed = form.breed.data
            animal.gender = form.gender.data
            animal.status = form.status.data
            db.session.commit()
            flash('Животное обновлено.', 'success')
            return redirect(url_for('routes.animal_detail', animal_id=animal.id, form=form))
        except:
            db.session.rollback()
            flash('Ошибка при обновлении животного.', 'danger')
    return render_template('animal_form.html', form=form, action="Редактировать")

@routes.route('/animal/<int:animal_id>/delete', methods=['POST'])
@login_required
def animal_delete(animal_id):
    if not current_user.is_admin():
        flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
        return redirect(url_for('routes.index'))

    animal = Animal.query.get_or_404(animal_id)
    try:
        for photo in animal.photos:
            path = os.path.join('static/uploads', photo.filename)
            if os.path.exists(path):
                os.remove(path)
        db.session.delete(animal)
        db.session.commit()
        flash('Животное удалено.', 'success')
    except:
        db.session.rollback()
        flash('Ошибка при удалении.', 'danger')
    return redirect(url_for('routes.index'))

@routes.route('/animal/<int:animal_id>')
def animal_detail(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    description_html = markdown.markdown(animal.description)
    requests = []
    user_request = None
    form = AdoptionForm()
    if current_user.is_authenticated:
        if current_user.is_staff():
            requests = AdoptionRequest.query.filter_by(animal_id=animal_id).order_by(AdoptionRequest.created_at.desc()).all()
        else:
            user_request = AdoptionRequest.query.filter_by(animal_id=animal_id, user_id=current_user.id).first()

    return render_template(
        'animal_detail.html',
        animal=animal,
        description_html=description_html,
        requests=requests,
        user_request=user_request,
        form=form
    )

@routes.route('/animal/<int:animal_id>/adopt', methods=['POST'])
@login_required
def animal_adopt(animal_id):
    if not current_user.is_user():
        flash('Только пользователи могут подавать заявки.', 'danger')
        return redirect(url_for('routes.index'))

    form = AdoptionForm()
    if form.validate_on_submit():
        already_sent = AdoptionRequest.query.filter_by(animal_id=animal_id, user_id=current_user.id).first()
        if already_sent:
            flash('Вы уже отправили заявку.', 'info')
            return redirect(url_for('routes.animal_detail', animal_id=animal_id, form=form))

        new_request = AdoptionRequest(
            animal_id=animal_id,
            user_id=current_user.id,
            contact_info=form.contact_info.data,
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Заявка успешно отправлена.', 'success')
    else:
        print(form.errors)
        flash('Ошибка при отправке заявки.', 'danger')
    return redirect(url_for('routes.animal_detail', animal_id=animal_id, form=form))

@routes.route('/request/<int:req_id>/<action>', methods=['POST'])
@login_required
def adoption_request_action(req_id, action):
    if not current_user.is_staff():
        flash('У вас недостаточно прав.', 'danger')
        return redirect(url_for('routes.index'))

    req = AdoptionRequest.query.get_or_404(req_id)
    if action == 'accept':
        req.status = 'accepted'
        req.animal.status = 'adopted'
        other = AdoptionRequest.query.filter(
            AdoptionRequest.animal_id == req.animal_id,
            AdoptionRequest.id != req.id,
            AdoptionRequest.status == 'pending'
        ).all()
        for r in other:
            r.status = 'rejected_adopted'
    elif action == 'reject':
        req.status = 'rejected'
    db.session.commit()
    flash('Статус заявки обновлён.', 'success')
    return redirect(url_for('routes.animal_detail', animal_id=req.animal_id))

@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user')
            db.session.add(user_role)
            db.session.commit()

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            login=form.login.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            role=user_role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)