import os
from flask import Flask, render_template, request
from flask import send_from_directory
from forms.forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
SMALL, BIG = 'small', 'big'
DESC = '''Мелодия из игры Отражение'''


class CurrentSet:
    menu_mode = SMALL


class Autor:
    name = 'Моккий Кифович'
    photo = 'static/users/User_phoenix.jpg'
    email = 'mokk@mail.ru'


class Publication:
    def __init__(self, filename, description, show_email=False):
        self.autor = Autor
        self.filename = 'static/users/' + filename
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
    return render_template('TitlePage.html', title='Главная', navigation=nav)


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = 'static/users/' + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
        return render_template('Account.html', title='Облако',
                               navigation=nav, menu=CurrentSet.menu_mode,
                               current_dir=current_dir, os=os,
                               sort_function=sort_function)
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function)


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
                           os=os)


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
                           publication=Publication(filename, ''))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    nav = [{'href': '/login', 'title': 'Войти'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    return render_template('Form.html', title='Регистрация', navigation=nav,
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    nav = [{'href': '/register', 'title': 'Регистрация'},
           {'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'}]
    return render_template('Form.html', title='Войти', navigation=nav,
                           form=form)


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
