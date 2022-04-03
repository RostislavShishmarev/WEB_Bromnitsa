from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, \
    SubmitField, EmailField, BooleanField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class RegisterForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    photo = FileField('Аватар',
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg',
                                               'webp', 'gif', 'ico'],
                                              'Неверный формат файла.'), ])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SettingsForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    photo = FileField('', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'svg',
                                                   'webp', 'gif', 'ico'],
                                                  'Неверный формат файла.'), ])
    submit = SubmitField('Применить')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired()])
    submit = SubmitField('Сменить пароль')
