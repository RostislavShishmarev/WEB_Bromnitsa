import os
import flask as fl
import requests as rq
from data import db_session as d_s
from data.publication import Publication
from flask import render_template, request
from forms.forms import MakePublicationForm
from helpers import Saver, TempPubl, Autor, sort_function, make_publ_file

app = fl.Flask(__name__)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
FILES_NUMBER = 2
SERVER = '127.0.0.1:8080'
publ_maker = Saver(description='', show_email=False)
publ_shower = Saver(current_index=0, string='')


@app.route('/favicon.ico')
def favicon():
    return fl.send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico',
                                  mimetype='image/vnd.microsoft.icon')


# TEST ><><><><
SMALL, BIG = 'small', 'big'


class flask_login:
    current_user = Autor


class CurrentSet:
    menu_mode = SMALL
# TEST ><><><>< ^


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
    if request.method == 'POST':
        if 'search_string' in request.form.keys():
            publ_shower.string = request.form['search_string'].lower()
    json_publs = rq.get('http://127.0.0.1:5000/publ_api' +\
                        ('/' + publ_shower.string
                         if publ_shower.string else '')).json()
    if request.method == 'POST':
        if 'next' in request.form.keys():
            if publ_shower.current_index + FILES_NUMBER < len(json_publs):
                publ_shower.current_index += FILES_NUMBER
        elif 'prev' in request.form.keys():
            if publ_shower.current_index - FILES_NUMBER >= 0:
                publ_shower.current_index -= FILES_NUMBER
    ind = publ_shower.current_index
    publs = json_publs[ind:ind + FILES_NUMBER]
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
    form = MakePublicationForm()
    if form.validate_on_submit():
        publ_maker.description = form.description.data
        publ_maker.show_email = form.show_email.data
    if request.method == 'POST':
        if 'public' in request.form.keys():
            db_sess = d_s.create_session()
            new_filename = make_publ_file(filename)
            publ = Publication(description=publ_maker.description,
                               show_email=publ_maker.show_email,
                               filename=new_filename,
                               user_id=flask_login.current_user.id)
            db_sess.add(publ)
            db_sess.commit()
            return fl.redirect('/publications')
    form.description.data = publ_maker.description
    form.show_email.data = publ_maker.show_email
    publ = TempPubl(filename, publ_maker.description, publ_maker.show_email)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=flask_login.current_user, form=form)


# TEST ><><><><
@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/publications', 'title': 'Публикации'},
           {'href': '/settings', 'title': 'Настройки'},
           {'href': '/logout', 'title': 'Выход'}]
    current_dir = 'static/users/1/cloud/' + current_dir.replace('&', '/')
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
    return render_template('Account.html', title='Облако',
                           navigation=nav, menu=CurrentSet.menu_mode,
                           current_dir=current_dir, os=os,
                           sort_function=sort_function,
                           current_user=flask_login.current_user)
# TEST ><><><>< ^


if __name__ == '__main__':
    d_s.global_init('db/cloud.db')
    app.run(port=int(SERVER.split(':')[1]), host=SERVER.split(':')[0])
