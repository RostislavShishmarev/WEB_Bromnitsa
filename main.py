import data.db_session as db_session
from data.users import User
from data.publication import Publication
import os
from flask import Flask, render_template, request
from flask import send_from_directory
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm,\
    MakePublicationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'

def main():
    db_session.global_init("db/cloud.sqlite")
    user1 = User(
        username='Artyom',
        email='test@test.com',
        photo='static/users/1/cloud/User_phoenix.jpg',
        path='static/users/1',

    )
    user1.set_password('123')
    db_sess = db_session.create_session()
    db_sess.add(user1)
    db_sess.commit()


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    db_session.global_init("db/cloud.db")
    user1 = User(
        username=form.name,
        email=form.email,
        photo=form.photo,
    )
    user1.set_password(form.password)
    user1.set_password('123')
    db_sess = db_session.create_session()
    db_sess.add(user1)
    db_sess.commit()
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/register', 'title': 'Регистрация'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        db_session.global_init("db/cloud.sqlite")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
    return render_template('Form.html', title='Авторизация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


if __name__ == '__main__':
    main()
    app.run(port=8080, host='127.0.0.1')
