import os
import flask as fl
import requests as rq
import flask_login
from flask import render_template, request
from forms.forms import MakePublicationForm
from helpers import Saver

app = fl.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)
FILES_NUMBER = 2
SERVER = '127.0.0.1:8080'
PUBL_API = '127.0.0.1:5000'
publ_maker = Saver(description='', show_email=False)
publ_shower = Saver(current_index=0, string='')


@app.route('/favicon.ico')
def favicon():
    return fl.send_from_directory(os.path.join(app.root_path, 'static'),
                                  'favicon.ico',
                                  mimetype='image/vnd.microsoft.icon')


class TempPubl:
    def __init__(self, filename, description, show_email=False,
                 author=flask_login.current_user):
        self.autor = author
        self.filename = flask_login.current_user.path + '/cloud/' + filename
        self.description = description
        self.show_email = show_email


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
    json_publs = rq.get('http://{}/publ_api'.format(PUBL_API) +\
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


@flask_login.login_required
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
            publ_dict = {
                'description': publ_maker.description,
                'filename': flask_login.current_user.path + '/cloud' +\
                            filename,
                'user_id': flask_login.current_user.id,
            }
            if publ_maker.show_email:
                publ_dict['show_email'] = publ_maker.show_email
            res = rq.post('http://{}/publ_api'.format(PUBL_API),
                          params=publ_dict).json()
            print(res)
            return fl.redirect('/publications')
    form.description.data = publ_maker.description
    form.show_email.data = publ_maker.show_email
    publ = TempPubl(filename, publ_maker.description, publ_maker.show_email)
    return render_template('Publication_maker.html',
                           title='Создать публикацию', navigation=nav, os=os,
                           publication=publ,
                           current_user=flask_login.current_user, form=form)
