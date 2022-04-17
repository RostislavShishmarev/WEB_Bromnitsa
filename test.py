import os
import data.db_session as db_session
from data.users import User
from data.publication import Publication
from flask import Flask, render_template, request, redirect
from flask import send_from_directory
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm,\
    MakePublicationForm
from flask_login import login_user
from flask_login import LoginManager
from flask_login import login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
app.config['JSON_AS_ASCII'] = False
login_manager = LoginManager()
login_manager.init_app(app)
SMALL, BIG = 'small', 'big'
USER_DIR = 'static/users/1/cloud/'
DESC = '''Мелодия из игры Отражение'''
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init("db/cloud.sqlite")
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class CurrentSet:
    menu_mode = SMALL


class Autor:
    name = 'Моккий Кифович'
    photo = 'static/users/1/cloud/User_phoenix.jpg'
    email = 'mokk@mail.ru'
    is_authenticated = True


class flask_login:
    current_user = Autor


'''class Publication:
    def __init__(self, filename, description, show_email=False):
        self.autor = Autor
        self.filename = USER_DIR + filename
        self.description = description
        self.show_email = show_email'''


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
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/publications', 'title': 'Публикации'}]
    db_session.global_init("db/cloud.sqlite")
    db_sess = db_session.create_session()
    '''if current_user.is_authenticated:
        publication = db_sess.query(Publication).filter(
            (Publication.author == current_user))
    else:
        publication = db_sess.query(Publication)'''
    return render_template('TitlePage.html', title='Главная', navigation=nav, current_user=flask_login.current_user)


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = USER_DIR + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
        return render_template('Account.html', title='Облако',
                               navigation=nav, menu=CurrentSet.menu_mode,
                               current_dir=current_dir, os=os,
                               sort_function=sort_function, current_user=flask_login.current_user)
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function, current_user=flask_login.current_user)


@app.route('/publications', methods=['GET', 'POST'])
def publications():
    if flask_login.current_user.is_authenticated:
        nav = [{'href': '/', 'title': 'Главная'},
               {'href': '/cloud', 'title': 'Облако'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    else:
        nav = [{'href': '/', 'title': 'Главная'},
               {'href': '/login', 'title': 'Войти'}]

    return render_template('Publications.html', title='Публикации',
                           navigation=nav,
                           publications=publs,
                           os=os, current_user=flask_login.current_user)


@app.route('/make_publication/<path:filename>',methods=['GET', 'POST'])
def make_publication(filename):
    filename = filename.replace('&', '/')
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=flask_login.current_user, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
        form = RegisterForm()
        nav = [{'href': '/login', 'title': 'Войти'},
               {'href': '/', 'title': 'Главная'},
               {'href': '/publications', 'title': 'Публикации'}]
        if form.validate_on_submit():
            db_session.global_init("db/cloud.sqlite")
            db_sess = db_session.create_session()
            user1 = User(
                username=form.name.data,
                email=form.email.data,
                photo=form.photo.data,
                password=form.password.data,
                path=USER_DIR
            )
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user:
                form.email.errors = "Вы уже зарегистрированы"
                return render_template('Form.html',
                                       message="Вы уже зарегистрированы",
                                       form=form)
            if form.password.data != form.password_again.data:
                form.password.errors = "Не совпадают пароли"
                return render_template('Form.html',
                                       message="Не совпадают пароли",
                                       form=form)
            db_sess.add(user1)
            db_sess.commit()
            a = f'static/users/{user1.id}/cloud'
            user1.path = a
            db_sess.add(user1)
            db_sess.commit()
            os.chdir('static/users')
            os.mkdir(str(user1.id))
            os.chdir(str(user1.id))
            os.mkdir('cloud')
            login_user(user1, remember=form.remember_me.data)
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
        db_session.global_init("db/cloud.sqlite")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember_me.data)
            return redirect("/settings")
        form.email.errors = "Неправильный логин или пароль"
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
        db_session.global_init("db/cloud.sqlite")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.email = form.email.data
        user.username = form.name.data
        user.photo = form.photo.data
        db_sess.add(user)
        db_sess.commit()
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
        form.password = "Пароли не совпадают"
        return render_template('Form.html',
                               message="Пароли не совпадают",
                               form=form)
    if form.validate_on_submit():
        db_session.global_init("db/cloud.sqlite")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.password = form.password.data
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
    return render_template('Form.html',
                           title='Удалить файл ' + filename.split('/')[-1],
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

    login_manager.login_view = 'login'
    app.run(port=8080, host='127.0.0.1')
