import os
import shutil
import flask as fl
import flask_login as fl_log
from flask_login import login_user
from flask import render_template, request, redirect, send_from_directory
from flask_restful import abort
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm,\
    MakePublicationForm

import data.db_session as db_session
from data.users import User
from data.publication import Publication
from helpers import Errors, CurrentSettings, alpha_sorter, time_sorter,\
    BAD_CHARS, format_name, make_file, make_photo, DEFAULT_PHOTO,\
    generate_secret_key, Saver, make_publ_file
from explorer import Explorer

app = fl.Flask(__name__)
app.config['SECRET_KEY'] = generate_secret_key()
app.config['JSON_AS_ASCII'] = False
login_manager = fl_log.LoginManager()
login_manager.init_app(app)
cloud_set = CurrentSettings()
PUBL_NUMBER = 6
publ_maker = Saver(description='', show_email=False)
publ_shower = Saver(current_index=0, string='')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@fl_log.login_required
def logout():
    global cloud_set
    fl_log.logout_user()
    cloud_set = CurrentSettings()
    return redirect("/")


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
        nav = [{'href': '/cloud', 'title': 'Облако'},
               {'href': '/publications', 'title': 'Публикации'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    return render_template('TitlePage.html', title='Главная', navigation=nav,
                           current_user=fl_log.current_user)


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def cloud(operpath=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = cloud_set.update_dir(operpath.replace('&', '/'),
                                       fl_log.current_user.path)
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            cloud_set.change_mode()
        elif 'filesubmit' in request.form.keys():
            files = request.files.getlist('file')
            for file in files:
                make_file(current_dir, file)
        elif 'search_string' in request.form.keys():
            cloud_set.string = request.form['search_string'].lower()
            cloud_set.current_index = 0
        elif 'sort_selector' in request.form.keys():
            if 'По названию' in request.form['sort_selector']:
                func = alpha_sorter
            else:
                func = time_sorter
            if request.form.get('reverse', False):
                cloud_set.reverse_files = True
            else:
                cloud_set.reverse_files = False
            cloud_set.sort_func = func
        elif 'next' in request.form.keys():
            n = len(cloud_set.sort_func(current_dir, cloud_set.string,
                                        cloud_set.reverse_files))
            if cloud_set.current_index + cloud_set.files_num < n:
                cloud_set.current_index += cloud_set.files_num
        elif 'prev' in request.form.keys():
            if cloud_set.current_index - cloud_set.files_num >= 0:
                cloud_set.current_index -= cloud_set.files_num
        else:
            exp = Explorer(fl_log.current_user)
            for key in request.form.keys():
                if key == 'copy-file':
                    name = request.form[key]
                    exp.copy(name)
                if key == 'cut-file':
                    name = request.form[key]
                    exp.cut(name)
                if key == 'paste_files':
                    exp.paste(current_dir)
    return render_template('Account.html', title='Облако',
                           navigation=nav, settings=cloud_set, os=os,
                           current_user=fl_log.current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    db_session.global_init("db/cloud.sqlite")
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

        path = 'static/users/' + str(user.id)
        user.path = path
        if not os.path.exists('static/users'):
            os.mkdir('static/users')
        for directory in ['', '/boofer', '/cloud', '/public', '/user_files']:
            os.mkdir(path + directory)
        photo = form.photo.data
        if photo:
            photoname = make_photo(photo, path)
            if photoname is None:
                db_sess.delete(user)
                db_sess.commit()
                form.photo.errors.append(Errors.BAD_FORMAT)
                return render_template('Form.html', title='Регистрация',
                                       navigation=nav, form=form,
                                       current_user=fl_log.current_user)
            user.photo = photoname
        db_sess.commit()
        login_user(user)
        return redirect('/')
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init("db/cloud.sqlite")
    form = LoginForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/register', 'title': 'Регистрация'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email ==\
                                          form.email.data).first()
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
        login_user(user)
        return redirect('/')
    return render_template('Form.html', title='Авторизация', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/settings', methods=['GET', 'POST'])
@fl_log.login_required
def settings():
    db_session.global_init("db/cloud.sqlite")
    form = SettingsForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        usrs = db_sess.query(User).filter(User.email == form.email.data).all()
        if len(usrs) >= 2:
            form.email.errors.append(Errors.USER_EXIST)
            return render_template('Settings.html', title='Настройки',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        user = db_sess.query(User).filter(User.id ==\
                                          fl_log.current_user.id).first()
        photo = form.photo.data
        if photo:
            photoname = make_photo(photo, fl_log.current_user.path)
            if photoname is None:
                form.photo.errors.append(Errors.BAD_FORMAT)
                return render_template('Settings.html', title='Настройки',
                                       navigation=nav, form=form,
                                       current_user=fl_log.current_user)
            user.photo = photoname
        user.username = form.name.data
        user.email = form.email.data
        db_sess.commit()
        # Чтобы увидеть изменения в том же окне.
        fl_log.logout_user()
        login_user(user)
    form.email.data = fl_log.current_user.email
    form.name.data = fl_log.current_user.username
    return render_template('Settings.html', title='Настройки', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/change_password', methods=['GET', 'POST'])
@fl_log.login_required
def change_password():
    db_session.global_init("db/cloud.sqlite")
    form = ChangePasswordForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
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


@app.route('/add_dir', methods=['GET', 'POST'])
@fl_log.login_required
def add_dir():
    form = MakeDirForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        dirname = form.name.data
        full = cloud_set.current_dir + '/' + dirname
        # Сначала именно символы
        incor_symb = BAD_CHARS & set(dirname)
        if incor_symb:
            form.name.errors.append(Errors.BAD_CHAR + '"' +\
                                    '", "'.join(incor_symb) + '"')
            return render_template('Form.html', title='Создать папку',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        if os.path.exists(full):
            form.name.errors.append(Errors.DIR_EXIST)
            return render_template('Form.html', title='Создать папку',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        os.mkdir(full)
        return redirect('/cloud/' +\
                        cloud_set.cur_dir_from_user.replace('/', '&'))
    return render_template('Form.html', title='Создать папку', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/rename/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def rename(operpath):
    filepath = operpath.replace('&', '/')
    full = format_name(fl_log.current_user.path + '/cloud/' + filepath)
    if not os.path.exists(full):
        abort(404, message='Файл не найден')
    filename = filepath.split('/')[-1]
    filetype = '.' + filename.split('.')[-1]
    form = RenameFileForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        new_name = form.name.data
        new_full = format_name(fl_log.current_user.path + '/cloud/' +\
                               filepath[:-len(filename)] + new_name)
        if os.path.isfile(full):
            new_full += filetype
        # Сначала именно символы
        incor_symb = BAD_CHARS & set(new_name)
        if incor_symb:
            form.name.errors.append(Errors.BAD_CHAR + '"' +\
                                    '", "'.join(incor_symb) + '"')
            return render_template('Form.html', title='Переименование',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        if os.path.exists(new_full) and full != new_full:
            form.name.errors.append(Errors.FILE_EXISTS)
            return render_template('Form.html', title='Переименование',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        os.rename(full, new_full)
        return redirect('/cloud/' +\
                        filepath[:-len(filename) - 1].replace('/', '&'))
    form.name.data = filename[:-len(filetype)] if os.path.isfile(full)\
        else filename
    return render_template('Form.html', title='Переименование',
                           navigation=nav, form=form,
                           current_user=fl_log.current_user)


@app.route('/delete/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def delete(operpath):
    filepath = operpath.replace('&', '/')
    full = format_name(fl_log.current_user.path + '/cloud/' + filepath)
    if not os.path.exists(full):
        abort(404, message='Файл не найден')
    filename = filepath.split('/')[-1]
    form = DeleteFileForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        if os.path.isfile(full):
            os.remove(full)
        else:
            shutil.rmtree(full)
        return redirect('/cloud/' +\
                        filepath[:-len(filename) - 1].replace('/', '&'))
    return render_template('Form.html',
                           title='Удалить ' + filename.split('/')[-1],
                           navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.before_request
def protector():
    path = request.path
    if not path.startswith('/static/users/'):
        return
    path = path[len('/static/users/'):]
    userdir, dir_, *list_path = path.split('/')
    user_path = 'static/users/' + userdir
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.path == user_path).first()
    if user:
        if dir_ in ['cloud', 'boofer']:
            if not fl_log.current_user.is_authenticated:
                abort(401, message='Вы не авторизованы')
            if user.id != fl_log.current_user.id:
                abort(403, message='У вас нет доступа к этим данным')
        return
    abort(404, message='Файл не найден')


class TempPubl:
    def __init__(self, filename, description, show_email=False,
                 author=fl_log.current_user):
        self.autor = author
        self.filename = fl_log.current_user.path + '/cloud/' + filename
        self.description = description
        self.show_email = show_email


@app.route('/publications', methods=['GET', 'POST'])
def publications():
    if fl_log.current_user.is_authenticated:
        nav = [{'href': '/', 'title': 'Главная'},
               {'href': '/cloud', 'title': 'Облако'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    else:
        nav = [{'href': '/login', 'title': 'Войти'},
               {'href': '/', 'title': 'Главная'}]

    if request.method == 'POST':
        if 'search_string' in request.form.keys():
            publ_shower.string = request.form['search_string'].lower()
    db_session.global_init("db/cloud.sqlite")
    db_sess = db_session.create_session()
    all_publs = db_sess.query(Publication).all()[::-1]
    filter_publs = [{'description': publ.description,
                     'file_name': publ.filename,
                     'show_email': publ.show_email,
                     'user_name': publ.author.username,
                     'user_photo': publ.author.photo,
                     'user_email': publ.author.email} for publ in all_publs
                    if check_publ(publ, publ_shower.string)]

    if request.method == 'POST':
        if 'next' in request.form.keys():
            if publ_shower.current_index + PUBL_NUMBER < len(filter_publs):
                publ_shower.current_index += PUBL_NUMBER
        elif 'prev' in request.form.keys():
            if publ_shower.current_index - PUBL_NUMBER >= 0:
                publ_shower.current_index -= PUBL_NUMBER
    ind = publ_shower.current_index
    sliced_publs = filter_publs[ind:ind + PUBL_NUMBER]
    return render_template('Publications.html', title='Публикации',
                           navigation=nav,
                           publications=sliced_publs,
                           os=os, current_user=fl_log.current_user)


def check_publ(publ, string):
    return string in publ.description.lower()or\
            string in publ.author.username.lower() or\
            string in publ.filename.split('/')[-1].lower()


@app.route('/make_publication/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def make_publication(operpath):
    db_session.global_init("db/cloud.sqlite")
    filename = operpath.replace('&', '/')
    full = format_name(fl_log.current_user.path + '/cloud/' + filename)
    if not os.path.exists(full) or not os.path.isfile(full):
        abort(404, message='Файл не найден')
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]

    form = MakePublicationForm()
    if form.validate_on_submit():
        publ_maker.description = form.description.data
        publ_maker.show_email = form.show_email.data

    if request.method == 'POST':
        if 'public' in request.form.keys():
            new_filename = make_publ_file(full)
            db_sess = db_session.create_session()
            publ = Publication(description=publ_maker.description,
                               show_email=publ_maker.show_email,
                               filename=new_filename,
                               user_id=fl_log.current_user.id)
            db_sess.add(publ)
            db_sess.commit()
            return fl.redirect('/publications')
    form.description.data = publ_maker.description
    form.show_email.data = publ_maker.show_email
    publ = TempPubl(filename, publ_maker.description, publ_maker.show_email)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=fl_log.current_user, form=form)


if __name__ == '__main__':
    db_session.global_init("db/cloud.sqlite")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
