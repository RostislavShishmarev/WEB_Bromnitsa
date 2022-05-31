from random import choices
from flask_restful import abort
from data import db_session as d_s
from data.users import User
from data.publication import Publication

DEFAULT_PHOTO = 'static/img/No_user.jpg'
SYMBOLS = list('1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJK\
LZXCVBNM')
USER_FIELDS = ['id', 'username', 'email', 'photo', 'path', 'password']
PUBL_FIELDS = ['id', 'description', 'filename', 'show_email', 'user_id',
               'modified_date']
SECRET_KEYS = [''.join(choices(SYMBOLS, k=50)) for _ in range(1)]
with open('secret_keys.txt', mode='w', encoding='utf8') as f:
    f.write('\n'.join(SECRET_KEYS))


def abort_if_no_user(user_id):
    sess = d_s.create_session()
    if not sess.query(User).get(user_id):
        abort(404, message='User with id {} isn`t found'.format(user_id))


def abort_if_wrong_email(email, user_id=None):
    db_sess = d_s.create_session()
    user = db_sess.query(User).filter(User.email == email).first()
    if user and (user_id is None or user_id != user.id):
        abort(400, message='Email {} already exists'.format(email))


def abort_if_wrong_item(item, items):
    if item not in items:
        abort(400, message='Type {} is not {}'.format(
            item, ' or '.join([str(i) for i in items])))


def abort_if_no_publ(publ_id):
    sess = d_s.create_session()
    if not sess.query(Publication).get(publ_id):
        abort(404, message='Publication with id {} \
isn`t found'.format(publ_id))


def abort_if_wrong_key(secret_key):
    if secret_key not in SECRET_KEYS:
        abort(403, message='Wrong secret key')
