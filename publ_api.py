import os
import flask as fl
from flask import render_template, request
from flask_restful import reqparse, abort, Api, Resource
from data import db_session as d_s
from data.publication import Publication

app = fl.Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'super_Seсret_key_of_devEl0pers'
SERVER = '127.0.0.1:5000'


class Autor:
    name = 'Моккий Кифович'
    photo = 'static/users/1/User_phoenix.jpg'
    email = 'mokk@mail.ru'
    is_authenticated = True


class flask_login:
    current_user = Autor


class Searcher(Resource):
    nav = [{'href': '/', 'title': 'Главная'},
           {'href': '/login', 'title': 'Войти'}]

    def get(self, search_string=''):
        db_sess = d_s.create_session()
        all_publs = db_sess.query(Publication).all()[::-1]
        filter_publs = [{'description': publ.description,
                         'file_name': publ.filename,
                         'show_email': publ.show_email,
                         'user_name': publ.author.username,
                         'user_photo': publ.author.photo,
                         'user_email': publ.author.email} for publ in all_publs
                        if self.check_publ(publ, search_string)]
        return fl.jsonify(filter_publs)

    def check_publ(self, publ, string):
        return string in publ.description.lower()or\
               string in publ.author.username.lower() or\
               string in publ.filename.split('/')[-1].lower()


api.add_resource(Searcher, '/publ_api/<search_string>', '/publ_api')
if __name__ == '__main__':
    d_s.global_init('db/cloud.db')
    app.run(port=int(SERVER.split(':')[1]), host=SERVER.split(':')[0])
