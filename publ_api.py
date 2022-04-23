import os
import flask as fl
from flask_restful import reqparse, abort, Api, Resource
from data import db_session as d_s
from data.publication import Publication
from data.users import User
from helpers import make_publ_file

app = fl.Flask(__name__)
api = Api(app)
with open('work_files/t.txt', encoding='utf8') as f:
    app.config['SECRET_KEY'] = f.read()
app.config['JSON_AS_ASCII'] = False

publ_parser = reqparse.RequestParser()
publ_parser.add_argument('description')
publ_parser.add_argument('filename', required=True)
publ_parser.add_argument('show_email', type=bool)
publ_parser.add_argument('user_id', required=True, type=int)


def abort_if_no_user(args):
    sess = d_s.create_session()
    if not sess.query(User).filter(User.id == args.user_id):
        abort(404, message='User with id {} \
isn`t found.'.format(args.user_id))


def abort_if_no_file(args):
    if not os.path.exists(args.filename):
        abort(404, message='File with path {} \
isn`t found.'.format(args.filename))


class PublApi(Resource):
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

    def post(self, search_string=''):
        args = publ_parser.parse_args()
        abort_if_no_user(args)
        abort_if_no_file(args)
        db_sess = d_s.create_session()
        new_filename = make_publ_file(args.filename)
        publ = Publication(description=args.description,
                           show_email=args.show_email,
                           filename=new_filename,
                           user_id=args.user_id)
        db_sess.add(publ)
        db_sess.commit()
        return fl.jsonify({'success': 'OK'})

    def check_publ(self, publ, string):
        return string in publ.description.lower()or\
               string in publ.author.username.lower() or\
               string in publ.filename.split('/')[-1].lower()


api.add_resource(PublApi, '/api/<search_string>', '/api')
if __name__ == '__main__':
    d_s.global_init('db/cloud.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
