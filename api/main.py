import os
import flask as fl
from flask_restful import abort, Api, Resource
from data import db_session as d_s
from data.publication import Publication
from data.users import User
from rq_parsers import publ_get_parser, only_key_parser, publ_post_parser, publ_put_parser
from helpers import generate_secret_key

app = fl.Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False
SECRET_KEYS = [generate_secret_key() for _ in range(1)]
with open('secret_keys.txt', mode='w', encoding='utf8') as f:
    f.write('\n'.join(SECRET_KEYS))
USER_FIELDS = ['username', 'email', 'photo', 'path', 'password']
PUBL_FIELDS = ['description', 'filename', 'show_email', 'user_id']


def abort_if_no_user(user_id):
    sess = d_s.create_session()
    if not sess.query(User).get(user_id):
        abort(404, message='User with id {} isn`t found.'.format(user_id))


def abort_if_no_publ(publ_id):
    sess = d_s.create_session()
    if not sess.query(Publication).get(publ_id):
        abort(404, message='Publication with id {} \
isn`t found.'.format(publ_id))


def abort_if_wrong_key(secret_key):
    if secret_key not in SECRET_KEYS:
        abort(403, message='Wrong secret key')


class UserResource(Resource):
    def get(self, user_id):
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(user_id)
        db_sess = d_s.create_session()
        user = db_sess.query(User).get(user_id)
        result = {field: getattr(user, field) for field in USER_FIELDS}
        return fl.jsonify(result)

    def put(self, user_id):
        pass

    def delete(self, user_id):
        pass


class UserListResource(Resource):
    def get(self):
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        db_sess = d_s.create_session()
        users = db_sess.query(User).all()
        result = [{field: getattr(user, field) for field in USER_FIELDS}
                  for user in users]
        return fl.jsonify(result)

    def post(self):
        pass


class BasePublResourse:
    def check_publ(self, publ, string):
        return string in publ.description.lower() or\
               string in publ.author.username.lower() or\
               string in publ.filename.split('/')[-1].lower()


class PublResource(Resource, BasePublResourse):
    def get(self, publ_id):
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        publ = db_sess.query(Publication).get(publ_id)
        result = {'id': publ.id,
                  'description': publ.description,
                  'file_name': publ.filename,
                  'show_email': publ.show_email,
                  'user_name': publ.author.username,
                  'user_photo': publ.author.photo,
                  'user_email': publ.author.email}
        return fl.jsonify(result)

    def put(self, publ_id):
        args = publ_put_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        publ = db_sess.query(Publication).get(publ_id)
        for field in PUBL_FIELDS:
            if field in args:
                val = args[field]
                if field == 'user_id':
                    abort_if_no_user(val)
                setattr(publ, field, val)
        db_sess.commit()
        return fl.jsonify({'success': 'OK'})

    def delete(self, publ_id):
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        db_sess.delete(db_sess.query(Publication).get(publ_id))
        db_sess.commit()
        return fl.jsonify({'success': 'OK'})


class PublListResource(Resource, BasePublResourse):
    def get(self):
        args = publ_get_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        db_sess = d_s.create_session()
        all_publs = db_sess.query(Publication).all()[::-1]
        filter_publs = [{'id': publ.id,
                         'description': publ.description,
                         'file_name': publ.filename,
                         'show_email': publ.show_email,
                         'user_name': publ.author.username,
                         'user_photo': publ.author.photo,
                         'user_email': publ.author.email} for publ in all_publs
                        if self.check_publ(publ, args.search_string)]
        return fl.jsonify(filter_publs)

    def post(self):
        args = publ_post_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(args.user_id)
        db_sess = d_s.create_session()
        publ = Publication(description=args.description,
                           show_email=args.show_email,
                           filename=args.filename,
                           user_id=args.user_id)
        db_sess.add(publ)
        db_sess.commit()
        return fl.jsonify({'success': 'OK'})


api.add_resource(UserApi, '/api/users')
api.add_resource(PublListResource, '/api/publications')
if __name__ == '__main__':
    d_s.global_init('../db/cloud.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
