from flask_restful import reqparse
from helpers import DEFAULT_PHOTO

only_key_parser = reqparse.RequestParser()
only_key_parser.add_argument('secret_key', required=True)

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('secret_key', required=True)
user_post_parser.add_argument('username', required=True)
user_post_parser.add_argument('email', required=True)
user_post_parser.add_argument('password', required=True)
user_post_parser.add_argument('photo', default=DEFAULT_PHOTO)

user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument('secret_key', required=True)
user_put_parser.add_argument('username')
user_put_parser.add_argument('email')
user_put_parser.add_argument('password')
user_put_parser.add_argument('photo')
user_put_parser.add_argument('path')

check_password_parser = reqparse.RequestParser()
check_password_parser.add_argument('secret_key', required=True)
check_password_parser.add_argument('password', required=True)

publ_get_parser = reqparse.RequestParser()
publ_get_parser.add_argument('secret_key', required=True)
publ_get_parser.add_argument('search_string', default='')

publ_post_parser = reqparse.RequestParser()
publ_post_parser.add_argument('secret_key', required=True)
publ_post_parser.add_argument('description', default='')
publ_post_parser.add_argument('filename', required=True)
publ_post_parser.add_argument('show_email', type=bool, default=False)
publ_post_parser.add_argument('user_id', required=True, type=int)

publ_put_parser = reqparse.RequestParser()
publ_put_parser.add_argument('secret_key', required=True)
publ_put_parser.add_argument('description')
publ_put_parser.add_argument('filename')
publ_put_parser.add_argument('show_email', type=bool)
publ_put_parser.add_argument('user_id', type=int)
