import os
import flask as fl
from flask_restful import abort, Api, Resource
from data import db_session as d_s
from data.publication import Publication
from data.users import User
from rq_parsers import publ_post_parser

app = fl.Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False


def abort_if_no_user(args):
    sess = d_s.create_session()
    if not sess.query(User).filter(User.id == args.user_id):
        abort(404, message='User with id {} \
isn`t found.'.format(args.user_id))



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
        args = publ_post_parser.parse_args()
        abort_if_no_user(args)
        db_sess = d_s.create_session()
        publ = Publication(description=args.description,
                           show_email=args.show_email,
                           filename=args.filename,
                           user_id=args.user_id)
        db_sess.add(publ)
        db_sess.commit()
        return fl.jsonify({'success': 'OK'})

    def check_publ(self, publ, string):
        return string in publ.description.lower() or\
               string in publ.author.username.lower() or\
               string in publ.filename.split('/')[-1].lower()


api.add_resource(PublApi, '/api/publ/<search_string>', '/api/publ')
if __name__ == '__main__':
    d_s.global_init('../db/cloud.sqlite')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
