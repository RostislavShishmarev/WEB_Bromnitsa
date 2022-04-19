import os
import shutil
import flask_login
from flask import Flask, render_template, request, redirect
from flask import send_from_directory
from flask_login import login_user
from flask_login import LoginManager
from flask_login import login_required, logout_user, current_user

import data.db_session as db_session
from data.users import User
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm

from publications import app as publ_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.init_app(app)

SMALL, BIG = 'small', 'big'
USER_PHOTO = 'static/img/No_user.jpg'


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init("db/cloud.sqlite")
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class CurrentSet:
    menu_mode = SMALL


class TempPubl:
    def __init__(self, filename, description, show_email=False,
                 author=flask_login.current_user):
        self.autor = author
        self.filename = flask_login.current_user.path + '/cloud/' + filename
        self.description = description
        self.show_email = show_email


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main_page():
    if flask_login.current_user.is_authenticated:
        nav = [{'href': '/publications', 'title': 'Публикации'},
               {'href': '/cloud', 'title': 'Облако'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    else:
        nav = [{'href': '/login', 'title': 'Войти'},
               {'href': '/publications', 'title': 'Публикации'}]
    return render_template('TitlePage.html', title='Главная', navigation=nav,
                           current_user=flask_login.current_user)


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    # if current_user.is_authenticated:
    # Если мы в облаке, то мы уже авторизованы.
    # Не забудь добавить @flask_login.login_required на такие страницы.
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    current_dir = user.path + '/cloud/' + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
        return render_template('Account.html', title='Облако',
                               navigation=nav, menu=CurrentSet.menu_mode,
                               current_dir=current_dir, os=os,
                               sort_function=sort_function,
                               current_user=flask_login.current_user,
                               current_index=0, files_num=6)
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function,
                           current_user=flask_login.current_user,
                           current_index=0, files_num=6)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            form.email.errors.append("Вы уже зарегистрированы")
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                           form=form, current_user=flask_login.current_user)
        if form.password.data != form.password_again.data:
            form.password.errors.append("Не совпадают пароли")
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                           form=form, current_user=flask_login.current_user)
        user = User(
            username=form.name.data,
            email=form.email.data,
            photo=USER_PHOTO
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        a = 'static/users/{}'.format(user.id)
        user.path = a
        os.mkdir(user.path)
        os.mkdir(user.path + '/cloud')
        os.mkdir(user.path + '/public')
        os.mkdir(user.path + '/user_files')
        f = form.photo.data
        if f:
            photoname = user.path + '/user_files/photo.' +\
                        f.filename.split('.')[-1]
            f.save(photoname)
            user.photo = photoname
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/")
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/register', 'title': 'Регистрация'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        form.email.errors.append("Неправильный логин или пароль")
        return render_template('Form.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('Form.html', title='Авторизация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.is_submitted():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.email = form.email.data
        user.username = form.name.data
        f = form.photo.data
        if f:
            photoname = user.path + '/user_files/photo.' + \
                        f.filename.split('.')[-1]
            f.save(photoname)
            user.photo = photoname
        db_sess.add(user)
        db_sess.commit()
        # Для отображения изменений тут же
        flask_login.logout_user()
        flask_login.login_user(user)
    #if type(current_user) == User:
    form.email.data = current_user.email
    form.name.data = current_user.username
    form.photo.data = current_user.photo

    return render_template('Settings.html', title='Настройки', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.password.data != form.password_again.data:
        form.password.errors = list(form.password.errors) +\
                               ["Пароли не совпадают"]
        return render_template('Form.html',
                               message="Пароли не совпадают",
                               form=form)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
    return render_template('Form.html', title='Сменить пароль', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/add_dir', methods=['GET', 'POST'])
def add_dir():
    form = MakeDirForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    if current_user.is_authenticated and form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        os.mkdir(user.path + '/cloud/' + form.name.data)
        return redirect('/cloud')
    return render_template('Form.html', title='Создать папку', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/rename_file/<path:filename>', methods=['GET', 'POST'])
def rename_file(filename):
    filename = filename.replace('&', '/')
    form = RenameFileForm()
    form.name.data = filename.split('/')[-1].split('.')[0]
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    if current_user.is_authenticated and form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        extension = '.' + filename.split('.')[1]
        print(extension)
        print(form.name.data)
        print(filename)
        '''os.chdir('static')
        os.chdir('users')
        os.chdir(str(user.id))
        os.chdir('user_files')
        os.rename(filename, form.name.data + extension)'''
        os.rename(user.path + '/cloud/' + filename, user.path + '/cloud/' + form.name.data + extension)
        return redirect('/cloud')
    return render_template('Form.html', title='Переименовать файл', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/delete_file/<path:filename>', methods=['GET', 'POST'])
def delete_file(filename):
    filename = filename.replace('&', '/')
    form = DeleteFileForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    if current_user.is_authenticated and form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        os.remove(user.path + '/cloud/' + filename)
        return redirect('/cloud')
    return render_template('Form.html',
                           title='Удалить файл ' + filename.split('/')[-1],
                           navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/copy_file/<path:filename>', methods=['GET', 'POST'])
def copy_file(filename):
    filename = filename.replace('&', '/')
    form = DeleteFileForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    if current_user.is_authenticated and form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        shutil.copy(user.path + '/cloud/' + filename, user.path + '/cloud/' + filename)
        return redirect('/cloud')
    return render_template('Form.html',
                           title='Копировать файл ' + filename.split('/')[-1],
                           navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/cut_file/<path:filename>', methods=['GET', 'POST'])
def cut_file(filename):
    filename = filename.replace('&', '/')
    form = DeleteFileForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    db_sess = db_session.create_session()
    if current_user.is_authenticated and form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        shutil.copy(user.path + '/cloud/' + filename, user.path + '/cloud/' + filename)
        os.remove(user.path + '/cloud/' + filename)
        return redirect('/cloud')
    return render_template('Form.html',
                           title='Вырезать файл ' + filename.split('/')[-1],
                           navigation=nav,
                           form=form, current_user=flask_login.current_user)


def sort_function(list_, cur_dir):
    key_sort = lambda x: x
    return sorted(list(filter(lambda f: os.path.isdir('/'.join([cur_dir,
                                                                f])), list_)),
                  key=key_sort) +\
           sorted(list(filter(lambda f: os.path.isfile('/'.join([cur_dir,
                                                                 f])), list_)),
                  key=key_sort)


if __name__ == '__main__':
    db_session.global_init("db/cloud.sqlite")
    login_manager.login_view = 'login'
    app.register_blueprint(publ_blueprint)
    app.run(port=8080, host='127.0.0.1')
