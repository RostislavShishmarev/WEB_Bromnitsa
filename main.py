import os
import flask as fl
import flask_login as fl_log
from flask import render_template, request, redirect, send_from_directory
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm

import data.db_session as db_session
from data.users import User
from helpers import Errors

app = fl.Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
app.config['JSON_AS_ASCII'] = False
SMALL, BIG = 'small', 'big'
DEFAULT_PHOTO = 'static/img/No_user.jpg'
login_manager = fl_log.LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@fl_log.login_required
@app.route('/logout')
def logout():
    fl_log.logout_user()
    return redirect("/")


class CurrentSet:
    menu_mode = SMALL


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main_page():
    if not fl_log.current_user.is_authenticated:
        nav = [{'href': '/login', 'title': 'Войти'},
               {'href': '/publications', 'title': 'Публикации'}]
    else:
        nav = [{'href': '/publications', 'title': 'Публикации'},
               {'href': '/cloud', 'title': 'Облако'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    return render_template('TitlePage.html', title='Главная', navigation=nav,
                           current_user=fl_log.current_user)


@fl_log.login_required
@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = fl_log.current_user.path + '/cloud' + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
        return render_template('Account.html', title='Облако',
                               navigation=nav, menu=CurrentSet.menu_mode,
                               current_dir=current_dir, os=os,
                               sort_function=sort_function, current_user=fl_log.current_user)
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function, current_user=fl_log.current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.password.data != form.password_again.data:
            form.password_again.errors.append(Errors.DIFF_PASS)
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                                   form=form, current_user=fl_log.current_user)
        if db_sess.query(User).filter(User.email == form.email.data).first():
            form.email.errors.append(Errors.USER_EXIST)
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                                   form=form, current_user=fl_log.current_user)
        user = User(
            username=form.name.data,
            email=form.email.data,
            photo=DEFAULT_PHOTO
        )
        user.set_password(form.password.data)

        # Отделено, чтобы узнать id пользователя
        db_sess.add(user)
        db_sess.commit()
        user = db_sess.query(User).filter(User.email == user.email).first()

        user.path = 'static/users/' + str(user.id)
        for directory in ['', '/boofer', '/cloud', '/public', '/user_files']:
            os.mkdir(user.path + directory)
        photo = form.photo.data
        if photo:
            user.photo = user.path + '/user_files/user_photo.' +\
                         photo.filename.split('.')[-1]
            photo.save(user.photo)

        db_sess.commit()
        fl_log.login_user(user)
        return redirect('/')
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/register', 'title': 'Регистрация'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            form.email.errors.append(Errors.NO_USER)
            return render_template('Form.html', title='Авторизация',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        if not user.check_password(form.password.data):
            form.password.errors.append(Errors.INCOR_PASS)
            return render_template('Form.html', title='Авторизация',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        fl_log.login_user(user)
        return redirect('/')
    return render_template('Form.html', title='Авторизация', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@fl_log.login_required
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        usrs = db_sess.query(User).filter(User.email == form.email.data).all()
        if len(usrs) >= 2:
            form.email.errors.append(Errors.USER_EXIST)
            return render_template('Settings.html', title='Настройки',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        photo = form.photo.data
        if photo:
            photo.save(fl_log.current_user.photo)
        user = db_sess.query(User).filter(User.id ==\
                                          fl_log.current_user.id).first()
        user.username = form.name.data
        user.email = form.email.data
        db_sess.commit()
        fl_log.logout_user()
        fl_log.login_user(user)
    form.email.data = fl_log.current_user.email
    form.name.data = fl_log.current_user.username
    return render_template('Settings.html', title='Настройки', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@fl_log.login_required
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.password.data != form.password_again.data:
            form.password_again.errors.append(Errors.DIFF_PASS)
            return render_template('Form.html', title='Сменить пароль',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        user = db_sess.query(User).filter(User.id ==\
                                          fl_log.current_user.id).first()
        user.set_password(form.password.data)
        db_sess.commit()
        return redirect('/')
    return render_template('Form.html', title='Сменить пароль', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@fl_log.login_required
@app.route('/add_dir', methods=['GET', 'POST'])
def add_dir():
    form = MakeDirForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    return render_template('Form.html', title='Создать папку', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@fl_log.login_required
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
                           form=form, current_user=fl_log.current_user)


@fl_log.login_required
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
                           form=form, current_user=fl_log.current_user)


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
    app.run(port=8080, host='127.0.0.1')
