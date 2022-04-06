import os
import flask as fl
from flask import render_template, request
from flask_restful import reqparse, abort, Api, Resource

app = fl.Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'


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


class Publications(Resource):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/login', 'title': 'Войти'}]

    def get(self, request=None):
        return render_template('Publications.html', title='Публикации',
                               navigation=Publications.nav,
                               publications=[],
                               os=os, current_user=flask_login.current_user)

    def post(self, request):
        if 'prev' in request.form.keys():
            print('previous!')
        elif 'next' in request.form.keys():
            pass
        elif 'search_string' in request.form.keys():
            string = request.form['search_string']
            pass
        return render_template('Publications.html', title='Публикации',
                               navigation=Publications.nav,
                               publications=[],
                               os=os, current_user=flask_login.current_user)
