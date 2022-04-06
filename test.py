import os
from flask import Flask, render_template, request
from flask import send_from_directory
from forms.forms import RegisterForm, LoginForm, SettingsForm,\
    ChangePasswordForm, MakeDirForm, RenameFileForm, DeleteFileForm,\
    MakePublicationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
app.config['JSON_AS_ASCII'] = False
SMALL, BIG = 'small', 'big'
USER_DIR = 'static/users/1/cloud/'
DESC = '''Мелодия из игры Отражение'''


class CurrentSet:
    menu_mode = SMALL


class Autor:
    name = 'Моккий Кифович'
    photo = 'static/users/1/cloud/User_phoenix.jpg'
    email = 'mokk@mail.ru'
    is_authenticated = True


class flask_login:
    current_user = Autor


class Publication:
    def __init__(self, filename, description, show_email=False):
        self.autor = Autor
        self.filename = USER_DIR + filename
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
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/login', 'title': 'Войти'}]
    return render_template('Publications.html', title='Публикации',
                           navigation=nav,
                           publications=[Publication('Exploding_block.png',
                                                     'Картинка взрывблока из \
                                                     игры "Отражение"'),
                                         Publication('play_fone.mp3',
                                                     DESC, True)],
                           os=os, current_user=flask_login.current_user)


@app.route('/make_publication/<path:filename>',methods=['GET', 'POST'])
def make_publication(filename):
    filename = filename.replace('&', '/')
    form = MakePublicationForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    print(filename)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=Publication(filename, ''),
                           current_user=flask_login.current_user, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/register', 'title': 'Регистрация'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    return render_template('Form.html', title='Авторизация', navigation=nav,
                           form=form, current_user=flask_login.current_user)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/cloud', 'title': 'Облако'},
           {'href': '/logout', 'title': 'Выход'}]
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
    app.run(port=8080, host='127.0.0.1')
