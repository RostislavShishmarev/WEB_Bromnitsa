from flask_restful import reqparse, inputs
from helpers import DEFAULT_PHOTO

only_key_parser = reqparse.RequestParser()
only_key_parser.add_argument('secret_key', type=str, required=True)

user_get_parser = reqparse.RequestParser()
user_get_parser.add_argument('secret_key', type=str, required=True)
user_get_parser.add_argument('email', type=str)
user_get_parser.add_argument('path', type=str)

user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('secret_key', type=str, required=True)
user_post_parser.add_argument('username', type=str, required=True)
user_post_parser.add_argument('email', type=str, required=True)
user_post_parser.add_argument('password', type=str, required=True)
user_post_parser.add_argument('photo', type=str, default=DEFAULT_PHOTO)

user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument('secret_key', type=str, required=True)
user_put_parser.add_argument('username', type=str)
user_put_parser.add_argument('email', type=str)
user_put_parser.add_argument('password', type=str)
user_put_parser.add_argument('photo', type=str)
user_put_parser.add_argument('path', type=str)

check_password_parser = reqparse.RequestParser()
check_password_parser.add_argument('secret_key', type=str, required=True)
check_password_parser.add_argument('password', type=str, required=True)

publ_get_parser = reqparse.RequestParser()
publ_get_parser.add_argument('secret_key', type=str, required=True)
publ_get_parser.add_argument('search_string', type=str, default='')

publ_post_parser = reqparse.RequestParser()
publ_post_parser.add_argument('secret_key', type=str, required=True)
publ_post_parser.add_argument('description', type=str, default='')
publ_post_parser.add_argument('filename', type=str, required=True)
publ_post_parser.add_argument('show_email', type=inputs.boolean, default=False)
publ_post_parser.add_argument('user_id', required=True, type=int)

publ_put_parser = reqparse.RequestParser()
publ_put_parser.add_argument('secret_key', type=str, required=True)
publ_put_parser.add_argument('description', type=str)
publ_put_parser.add_argument('filename', type=str)
publ_put_parser.add_argument('show_email', type=inputs.boolean)
publ_put_parser.add_argument('user_id', type=int)
