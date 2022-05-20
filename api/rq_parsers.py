from flask_restful import reqparse

publ_post_parser = reqparse.RequestParser()
publ_post_parser.add_argument('description')
publ_post_parser.add_argument('filename', required=True)
publ_post_parser.add_argument('show_email', type=bool)
publ_post_parser.add_argument('user_id', required=True, type=int)
