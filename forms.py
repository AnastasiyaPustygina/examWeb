from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, SelectField, MultipleFileField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from models import User

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')

class AnimalForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=100)])
    breed = StringField('Порода', validators=[DataRequired(), Length(max=100)])
    age = IntegerField('Возраст (месяцев)', validators=[DataRequired()])
    gender = SelectField('Пол', choices=[('M','Мужской'),('F','Женский')], validators=[DataRequired()])
    status = SelectField('Статус', choices=[('available','Доступно'),('adoption','Усыновление'),('adopted','Усыновлено')])
    description = TextAreaField('Описание', validators=[DataRequired()])
    images = MultipleFileField('Фото')

class AdoptionForm(FlaskForm):
    contact_info = TextAreaField('Контактные данные', validators=[DataRequired(), Length(max=200)])

class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество (необязательно)')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Этот логин уже занят. Пожалуйста, выберите другой.')