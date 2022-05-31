import os
import flask as fl
import logging as lg
from flask_restful import Api, Resource, abort
from data import db_session as d_s
from data.users import User
from data.publication import Publication
from rq_parsers import only_key_parser, publ_get_parser, publ_post_parser,\
    publ_put_parser, user_get_parser, user_post_parser, user_put_parser,\
    check_password_parser
from helpers import abort_if_no_user, abort_if_no_publ,abort_if_wrong_key,\
    abort_if_wrong_email, abort_if_wrong_item, USER_FIELDS, PUBL_FIELDS

app = fl.Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False
lg.basicConfig(level='DEBUG',
               format='%(asctime)s %(levelname)s %(filename)s %(message)s')


class UserResource(Resource):
    def get(self, user_id):
        d_s.global_init('db/cloud.sqlite')
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(user_id)
        db_sess = d_s.create_session()
        user = db_sess.query(User).get(user_id)
        result = {field: getattr(user, field) for field in USER_FIELDS}
        return fl.jsonify(result)

    def put(self, user_id):
        d_s.global_init('db/cloud.sqlite')
        args = user_put_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(user_id)
        db_sess = d_s.create_session()
        user = db_sess.query(User).get(user_id)
        lg.debug('PUT in users:')
        for field in USER_FIELDS:
            if field in args:
                val = args[field]
                if val is None:
                    continue
                lg.debug('>>  {}: {} -- start'.format(field,
                                                      getattr(user, field)))
                if field == 'password':
                    user.set_password(val)
                    continue
                elif field == 'email':
                    abort_if_wrong_email(val, user_id=user_id)
                setattr(user, field, val)
                lg.debug('    {}: {} -- end'.format(field, val))
        db_sess.commit()
        return fl.jsonify({'success': True})

    def delete(self, user_id):
        d_s.global_init('db/cloud.sqlite')
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(user_id)
        db_sess = d_s.create_session()
        user = db_sess.query(User).get(user_id)
        db_sess.delete(user)
        db_sess.commit()
        return fl.jsonify({'success': True})


class UserListResource(Resource):
    def get(self):
        d_s.global_init('db/cloud.sqlite')
        args = user_get_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        db_sess = d_s.create_session()
        if args.email is not None:
            user = db_sess.query(User).filter(User.email == args.email).first()
            result = {field: getattr(user, field) for field in USER_FIELDS
                      if user is not None}
            return fl.jsonify(result if result else None)
        elif args.path is not None:
            user = db_sess.query(User).filter(User.path == args.path).first()
            result = {field: getattr(user, field) for field in USER_FIELDS
                      if user is not None}
            return fl.jsonify(result if result else None)
        else:
            users = db_sess.query(User).all()
            result = [{field: getattr(user, field) for field in USER_FIELDS}
                      for user in users]
            return fl.jsonify(result)

    def post(self):
        d_s.global_init('db/cloud.sqlite')
        args = user_post_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_wrong_email(args.email)
        db_sess = d_s.create_session()
        user = User(
            username=args.username,
            email=args.email,
            photo=args.photo,
            path=''
        )
        user.set_password(args.password)
        db_sess.add(user)
        user_with_id = db_sess.query(User).filter(User.email ==
                                                  args.email).first()
        path = 'static/users/' + str(user_with_id.id)
        user_with_id.path = path
        db_sess.commit()
        return fl.jsonify({'success': True})


class CheckUserResource(Resource):
    def get(self, user_id):
        d_s.global_init('db/cloud.sqlite')
        args = check_password_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_user(user_id)
        db_sess = d_s.create_session()
        user = db_sess.query(User).get(user_id)
        return fl.jsonify({'success': user.check_password(args.password)})


class UserGetByResource(Resource):
    def get(self, item):
        d_s.global_init('db/cloud.sqlite')
        args = user_get_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        items = ['email', 'path']
        abort_if_wrong_item(item, items)
        db_sess = d_s.create_session()
        val = getattr(args, item)
        if val is None:
            abort(400, message='No parameter {}'.format(item))
        user = db_sess.query(User).filter(getattr(User, item) == val).first()
        result = {field: getattr(user, field) for field in USER_FIELDS
                  if user is not None}
        return fl.jsonify(result if result else None)


class BasePublResourse:
    def check_publ(self, publ, string):
        return string in publ.description.lower() or\
               string in publ.author.username.lower() or\
               string in publ.filename.split('/')[-1].lower()


class PublResource(Resource, BasePublResourse):
    def get(self, publ_id):
        d_s.global_init('db/cloud.sqlite')
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        publ = db_sess.query(Publication).get(publ_id)
        dict_ = {field: getattr(publ, field) for field in PUBL_FIELDS
                 if field != 'user_id'}
        dict_['author'] = {field: getattr(publ.author, field)
                           for field in USER_FIELDS}
        return fl.jsonify(dict_)

    def put(self, publ_id):
        d_s.global_init('db/cloud.sqlite')
        args = publ_put_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        publ = db_sess.query(Publication).get(publ_id)
        lg.debug('PUT in publications:')
        for field in PUBL_FIELDS:
            if field in args:
                val = args[field]
                if val is None:
                    continue
                lg.debug('>>  {}: {} -- start'.format(field,
                                                      getattr(publ, field)))
                if field == 'user_id':
                    abort_if_no_user(val)
                setattr(publ, field, val)
                lg.debug('    {}: {} -- end'.format(field, val))
        db_sess.commit()
        return fl.jsonify({'success': True})

    def delete(self, publ_id):
        d_s.global_init('db/cloud.sqlite')
        args = only_key_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        abort_if_no_publ(publ_id)
        db_sess = d_s.create_session()
        db_sess.delete(db_sess.query(Publication).get(publ_id))
        db_sess.commit()
        return fl.jsonify({'success': True})


class PublListResource(Resource, BasePublResourse):
    def get(self):
        d_s.global_init('db/cloud.sqlite')
        args = publ_get_parser.parse_args()
        abort_if_wrong_key(args.secret_key)
        db_sess = d_s.create_session()
        all_publs = db_sess.query(Publication).all()[::-1]
        filtered_publs = []
        for publ in all_publs:
            if self.check_publ(publ, args.search_string):
                dict_ = {field: getattr(publ, field) for field in PUBL_FIELDS
                         if field != 'user_id'}
                dict_['author'] = {field: getattr(publ.author, field)
                                   for field in USER_FIELDS}
                filtered_publs += [dict_, ]
        return fl.jsonify(filtered_publs)

    def post(self):
        d_s.global_init('db/cloud.sqlite')
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
        return fl.jsonify({'success': True})


api.add_resource(UserListResource, '/api/users')
api.add_resource(UserResource, '/api/users/<int:user_id>')
api.add_resource(CheckUserResource, '/api/users/check_password/<int:user_id>')
api.add_resource(UserGetByResource, '/api/users/get_by/<string:item>')
api.add_resource(PublListResource, '/api/publications')
api.add_resource(PublResource, '/api/publications/<int:publ_id>')

if __name__ == '__main__':
    d_s.global_init('db/cloud.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
