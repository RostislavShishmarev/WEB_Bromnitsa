import os
import shutil
import requests as rq
import flask as fl
import flask_login as fl_log
from flask_login import login_user
from flask import render_template, request, redirect, send_from_directory
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm,\
    MakePublicationForm

from helpers import lg, Errors, CloudSettings,\
    BAD_CHARS, format_name, make_file, make_photo, DEFAULT_PHOTO,\
    generate_secret_key, get_func, FuncHolder, DEFAULT_CLOUD_SET,\
    Api, FileFormatError, TempUser, TempPubl, make_publ_file, PUBL_NUMBER,\
    BaseSettings
from explorer import Explorer

app = fl.Flask(__name__)
key = generate_secret_key()
app.config['SECRET_KEY'] = key
app.config['JSON_AS_ASCII'] = False
login_manager = fl_log.LoginManager()
login_manager.init_app(app)
cloud_set = CloudSettings('cloud_set', DEFAULT_CLOUD_SET)
publ_maker = BaseSettings('publ_maker', {'description': '',
                                         'show_email': False})
publ_shower = BaseSettings('publ_shower', {'current_index': 0, 'string': ''})



@login_manager.user_loader
def load_user(user_id):
    res = rq.get(Api.SERVER + '/users/' + str(user_id), params={
        'secret_key': Api.KEY,
    })
    return TempUser(res.json())


@app.route('/logout')
@fl_log.login_required
def logout():
    fl_log.logout_user()
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
    lg.debug('><><><>< RELOAD cloud window ><><><><')
    lg.debug('flask.session (BEGIN): {}'.format(fl.session))
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
                try:
                    make_file(current_dir, file)
                except FileFormatError as ex:
                    pass
        elif 'search_string' in request.form.keys():
            cloud_set.string = request.form['search_string'].lower()
            cloud_set.current_index = 0
        elif 'sort_selector' in request.form.keys():
            if 'По названию' in request.form['sort_selector']:
                func_type = 'alpha'
            else:
                func_type = 'time'
            if request.form.get('reverse', False):
                cloud_set.reverse_files = True
            else:
                cloud_set.reverse_files = False
            cloud_set.func_type = func_type
        elif 'next' in request.form.keys():
            func = get_func(cloud_set.func_type)
            n = len(func(current_dir, cloud_set.string,
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
    holder = FuncHolder(get_func(cloud_set.func_type))
    lg.debug('flask.session (END): {}'.format(fl.session))
    return render_template('Account.html', title='Облако',
                           navigation=nav, settings=cloud_set.serialized(),
                           func_holder=holder,
                           os=os, current_user=fl_log.current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password_again.errors.append(Errors.DIFF_PASS)
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                                   form=form, current_user=fl_log.current_user)
        user = TempUser(rq.get(Api.SERVER + '/users/get_by/email', params={
            'secret_key': Api.KEY,
            'email': form.email.data}).json())
        if user:
            form.email.errors.append(Errors.USER_EXIST)
            return render_template('Form.html', title='Регистрация',
                                   navigation=nav,
                                   form=form, current_user=fl_log.current_user)
        res = rq.post(Api.SERVER + '/users', params={
            'secret_key': Api.KEY,
            'username': form.name.data,
            'email': form.email.data,
            'photo': DEFAULT_PHOTO,
            'password': form.password.data
        })

        # Отделено для создания нужных директорий и файлов
        user = TempUser(rq.get(Api.SERVER + '/users', params={
            'secret_key': Api.KEY,
            'email': form.email.data}).json())

        path = user.path
        if not os.path.exists('static/users'):
            os.mkdir('static/users')
        for directory in ['', '/boofer', '/cloud', '/public', '/user_files']:
            os.mkdir(path + directory)
        photo_file = form.photo.data
        if photo_file:
            try:
                photoname = make_photo(photo_file, path)
            except FileFormatError as ex:
                rq.delete(Api.SERVER + '/users/' + str(user.id), params={
                    'secret_key': Api.KEY
                })
                form.photo.errors.append(Errors.BAD_FORMAT)
                return render_template('Form.html', title='Регистрация',
                                       navigation=nav, form=form,
                                       current_user=fl_log.current_user)
            res = rq.put(Api.SERVER + '/users/' + str(user.id),
                         params={'secret_key': Api.KEY,
                                 'photo': photoname})
        login_user(user)
        return redirect('/')
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/register', 'title': 'Регистрация'}]
    if form.validate_on_submit():
        user = TempUser(rq.get(Api.SERVER + '/users/get_by/email', params={
            'secret_key': Api.KEY,
            'email': form.email.data}).json())
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
    form = SettingsForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        user = TempUser(rq.get(Api.SERVER + '/users/get_by/email', params={
            'secret_key': Api.KEY,
            'email': form.email.data}).json())
        if user and user.id != fl_log.current_user.id:
            form.email.errors.append(Errors.USER_EXIST)
            return render_template('Settings.html', title='Настройки',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        photo = form.photo.data
        photoname = fl_log.current_user.photo
        if photo:
            try:
                photoname = make_photo(photo, fl_log.current_user.path)
            except FileFormatError as ex:
                form.photo.errors.append(Errors.BAD_FORMAT)
                return render_template('Settings.html', title='Настройки',
                                       navigation=nav, form=form,
                                       current_user=fl_log.current_user)
        lg.debug('Создание фото. Путь: {}'.format(photoname))
        res = rq.put(Api.SERVER + '/users/' + str(fl_log.current_user.id),
                     params={'secret_key': Api.KEY,
                             'photo': photoname,
                             'username': form.name.data,
                             'email': form.email.data})
        id_ = fl_log.current_user.id
        fl_log.logout_user()  # Чтобы увидеть изменения в том же окне.
        user = TempUser(rq.get(Api.SERVER + '/users/' + str(id_),
                               params={'secret_key': Api.KEY}).json())
        login_user(user)
    form.email.data = fl_log.current_user.email
    form.name.data = fl_log.current_user.username
    return render_template('Settings.html', title='Настройки', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/change_password', methods=['GET', 'POST'])
@fl_log.login_required
def change_password():
    form = ChangePasswordForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password_again.errors.append(Errors.DIFF_PASS)
            return render_template('Form.html', title='Сменить пароль',
                                   navigation=nav, form=form,
                                   current_user=fl_log.current_user)
        res = rq.put(Api.SERVER + '/users/' + str(fl_log.current_user.id),
                     params={'secret_key': Api.KEY,
                             'password': form.password.data})
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
            form.name.errors.append(Errors.BAD_CHAR + '"' +
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
        return redirect('/cloud/' +
                        cloud_set.cur_dir_from_user.replace('/', '&'))
    return render_template('Form.html', title='Создать папку', navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/rename/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def rename(operpath):
    filepath = operpath.replace('&', '/')
    full = format_name(fl_log.current_user.path + '/cloud/' + filepath)
    if not os.path.exists(full):
        fl.abort(404, message='Файл не найден')
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
        new_full = format_name(fl_log.current_user.path + '/cloud/' +
                               filepath[:-len(filename)] + new_name)
        if os.path.isfile(full):
            new_full += filetype
        # Сначала именно символы
        incor_symb = BAD_CHARS & set(new_name)
        if incor_symb:
            form.name.errors.append(Errors.BAD_CHAR + '"' +
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
        return redirect('/cloud/' +
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
        fl.abort(404, message='Файл не найден')
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
        return redirect('/cloud/' +
                        filepath[:-len(filename) - 1].replace('/', '&'))
    return render_template('Form.html',
                           title='Удалить ' + filename.split('/')[-1],
                           navigation=nav,
                           form=form, current_user=fl_log.current_user)


@app.route('/publications', methods=['GET', 'POST'])
def publications():
    if fl_log.current_user.is_authenticated:
        nav = [{'href': '/', 'title': 'Главная'},
               {'href': '/cloud', 'title': 'Облако'},
               {'href': '/settings', 'title': 'Настройки'},
               {'href': '/logout', 'title': 'Выход'}]
    else:
        nav = [{'href': '/', 'title': 'Главная'},
               {'href': '/login', 'title': 'Войти'}]

    if request.method == 'POST':
        if 'search_string' in request.form.keys():
            publ_shower.string = request.form['search_string'].lower()
    json_publs = rq.get(Api.SERVER + '/publications', params={
        'secret_key': Api.KEY,
        'search_string': publ_shower.string
    }).json()

    if request.method == 'POST':
        if 'next' in request.form.keys():
            if publ_shower.current_index + PUBL_NUMBER < len(json_publs):
                publ_shower.current_index += PUBL_NUMBER
        elif 'prev' in request.form.keys():
            if publ_shower.current_index - PUBL_NUMBER >= 0:
                publ_shower.current_index -= PUBL_NUMBER
    ind = publ_shower.current_index
    publs = json_publs[ind:ind + PUBL_NUMBER]

    return render_template('Publications.html', title='Публикации',
                           navigation=nav,
                           publications=publs,
                           os=os, current_user=fl_log.current_user)


@app.route('/make_publication/<path:operpath>', methods=['GET', 'POST'])
@fl_log.login_required
def make_publication(operpath):
    filename = operpath.replace('&', '/')
    full = format_name(fl_log.current_user.path + '/cloud/' + filename)
    if not os.path.exists(full) or not os.path.isfile(full):
        fl.abort(404, 'Файл не найден')
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
            res = rq.post(Api.SERVER + '/publications', params={
                'secret_key': Api.KEY,
                'description': publ_maker.description,
                'filename': make_publ_file(fl_log.current_user.path +
                                           '/cloud/' + filename),
                'user_id': fl_log.current_user.id,
                'show_email': publ_maker.show_email
            }).json()
            return fl.redirect('/publications')
    form.description.data = publ_maker.description
    form.show_email.data = publ_maker.show_email
    publ = TempPubl(filename, publ_maker.description, fl_log.current_user,
                    show_email=publ_maker.show_email)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=fl_log.current_user, form=form)


@app.before_request
def protector():
    path = request.path
    if not path.startswith('/static/users/'):
        return
    path = path[len('/static/users/'):]
    list_path = path.split('/')
    userdir = list_path[0] if list_path else ''
    dir_ = list_path[1] if len(list_path) >= 2 else ''
    user_path = 'static/users/' + userdir
    user = TempUser(rq.get(Api.SERVER + '/users/get_by/path', params={
        'secret_key': Api.KEY,
        'path': user_path}).json())
    if user:
        if dir_ in ['cloud', 'boofer']:
            if not fl_log.current_user.is_authenticated:
                fl.abort(401, 'Вы не авторизованы')
            if user.id != fl_log.current_user.id:
                fl.abort(403, 'У вас нет доступа к этим данным')
        return
    fl.abort(404, 'Файл не найден')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
