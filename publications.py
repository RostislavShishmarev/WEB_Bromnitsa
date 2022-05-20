import os
import flask as fl
import requests as rq
import flask_login
from flask import render_template, request
from flask_restful import abort
from forms.forms import MakePublicationForm
from helpers import Saver, format_name, make_publ_file

app = fl.Blueprint('news_api',  __name__, template_folder='templates')
PUBL_NUMBER = 6
PUBL_API = '127.0.0.1:5000/api/publ'
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


def abort_if_no_file(args):
    if not os.path.exists(args.filename):
        abort(404, message='File with path {} \
isn`t found.'.format(args.filename))


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
    json_publs = rq.get('http://{}'.format(PUBL_API) +
                        ('/' + publ_shower.string
                         if publ_shower.string else '')).json()

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
                           os=os, current_user=flask_login.current_user)


@app.route('/make_publication/<path:operpath>', methods=['GET', 'POST'])
@flask_login.login_required
def make_publication(operpath):
    filename = operpath.replace('&', '/')
    full = format_name(flask_login.current_user.path + '/cloud/' + filename)
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
            path = flask_login.current_user.path
            publ_dict = {
                'description': publ_maker.description,
                'filename': make_publ_file(path + '/cloud/' + filename),
                'user_id': flask_login.current_user.id,
            }
            if publ_maker.show_email:
                publ_dict['show_email'] = publ_maker.show_email
            res = rq.post('http://{}'.format(PUBL_API),
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
