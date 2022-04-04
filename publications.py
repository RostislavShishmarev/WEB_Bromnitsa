import os
from data import db_session as d_s
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon',
                               current_user=flask_login.current_user)


class Autor:
    name = 'Моккий Кифович'
    photo = 'static/users/1/User_phoenix.jpg'
    email = 'mokk@mail.ru'
    is_authenticated = True


class flask_login:
    current_user = Autor


class Publication:
    def __init__(self, filename, description, show_email=False):
        self.autor = flask_login.current_user
        self.filename = 'static/users/1/' + filename
        self.description = description
        self.show_email = show_email


@app.route('/publications', methods=['GET', 'POST'])
def publications():
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/login', 'title': 'Войти'}]
    if request.method == 'POST':
        pass
    return render_template('Publications.html', title='Публикации',
                           navigation=nav,
                           publications=[],
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
                           publication=Publication(filename, ''),
                           current_user=flask_login.current_user)


if __name__ == '__main__':
    d_s.global_init('db/cloud.db')
    app.run(port=8080, host='127.0.0.1')
