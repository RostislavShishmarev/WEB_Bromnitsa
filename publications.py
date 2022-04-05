import os
import flask as fl
from data import db_session as d_s
from data.publication import Publication
from flask import render_template, request
from forms.forms import MakePublicationForm

app = fl.Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'


@app.route('/favicon.ico')
def favicon():
    return fl.send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico',
                                  mimetype='image/vnd.microsoft.icon')


class Saver:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


publ_maker = Saver(description='', show_email=False)


class Autor:
    id = 1
    name = 'Моккий Кифович'
    photo = 'static/users/1/User_phoenix.jpg'
    password = 'hoorey!'
    email = 'mokk@mail.ru'
    is_authenticated = True


class flask_login:
    current_user = Autor


class TestPublication:
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
        if 'prev' in request.form.keys():
            pass
        elif 'next' in request.form.keys():
            pass
        elif 'search_string' in request.form.keys():
            string = request.form['search_string']
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
    form = MakePublicationForm()
    if form.validate_on_submit():
        publ_maker.description = form.description.data
        publ_maker.show_email = form.show_email.data
    if request.method == 'POST':
        if 'public' in request.form.keys():
            db_sess = d_s.create_session()
            publ = Publication(description=publ_maker.description,
                               show_email=publ_maker.show_email,
                               filename=filename,
                               user_id=flask_login.current_user.id)
            db_sess.add(publ)
            db_sess.commit()
            return fl.redirect('/publications')
    form.description.data = publ_maker.description
    form.show_email.data = publ_maker.show_email
    publ = TestPublication(filename, publ_maker.description, publ_maker.show_email)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=flask_login.current_user, form=form)


SMALL, BIG = 'small', 'big'


class CurrentSet:
    menu_mode = SMALL


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = 'static/users/1/' + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function, current_user=flask_login.current_user)


def sort_function(list_, cur_dir):
    key_sort = lambda x: x
    return sorted(list(filter(lambda f: os.path.isdir('/'.join([cur_dir,
                                                                f])), list_)),
                  key=key_sort) +\
           sorted(list(filter(lambda f: os.path.isfile('/'.join([cur_dir,
                                                                 f])), list_)),
                  key=key_sort)


if __name__ == '__main__':
    d_s.global_init('db/cloud.db')
    app.run(port=8080, host='127.0.0.1')
