import os
import shutil
import flask as fl
import logging as lg
import requests as rq
from flask_login import UserMixin
from random import choices
from csv import DictReader

# Константы и сборники констант
LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s %(message)s'
IMAGE_TYPES = ('jpg', 'jpeg', 'png', 'svg', 'webp', 'gif', 'ico')
BAD_CHARS = {' ', '/', '\\', '&', '?', '@', '"', "'", '(', ')'}
DEFAULT_PHOTO = 'static/img/No_user.jpg'
SYMBOLS = '1234567890!@#$%^&*()~`-=_+ qwertyuiop[]asdfghjkl;zxcvbnm,./\
QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?'
DEFAULT_CLOUD_SET = {'current_dir': '', 'cur_dir_from_user': '',
                     'menu_mode': 'small', 'out_of_root': False, 'string': '',
                     'func_type': 'alpha', 'reverse_files': False,
                     'current_index': 0, 'files_num': 10}
PUBL_NUMBER = 6

lg.basicConfig(level='DEBUG', format=LOG_FORMAT)


class Api:
    with open('settings.csv', encoding='utf8') as f:
        settings = list(DictReader(f, delimiter=';', quotechar='"'))[0]
    SERVER = settings['api_server']
    with open('api/secret_keys.txt', encoding='utf8') as f:
        keys = f.read().split('\n')
    KEY = keys[0]


class Errors:
    USER_EXIST = "Такой пользователь уже есть"
    DIFF_PASS = 'Пароли не совпадают'
    NO_USER = "Такого пользователя не существует"
    INCOR_PASS = "Неверный пароль"
    DIR_EXIST = "Такая директория уже есть"
    FILE_EXISTS = "Такой файл уже есть."
    BAD_CHAR = "Встречаются недопустимые символы: "
    BAD_FORMAT = "Некорректный формат файла."


# Вспомогательные классы
class FuncHolder:
    def __init__(self, func):
        self.sort_func = func


class BaseSettings:
    def __init__(self, name, base):
        self.__dict__['name'] = name
        self.__dict__['base'] = base

    def _make_dict_if_not_exists(self):
        if self.name not in fl.session.keys():
            lg.debug('{} dict has remade'.format(self.name))
            fl.session[self.name] = self.base

    def __setattr__(self, key, value):
        self._make_dict_if_not_exists()
        fl.session[self.name][key] = value
        fl.session.modified = True

    def __getattr__(self, item):
        self._make_dict_if_not_exists()
        return fl.session[self.name][item]

    def serialized(self):
        self._make_dict_if_not_exists()
        lg.debug('Serializing {}'.format(self.name))
        return fl.session[self.name]

    def log_self(self):
        self._make_dict_if_not_exists()
        lg.debug('SETTINGS DATA: \n  flask.session["{}"]:\n  >> {}'.format(
            self.name, '\n  >> '.join(['{}: {}'.format(k, v)
                                       for k, v in fl.session[
                                           self.name].items()])))


class CloudSettings(BaseSettings):
    SMALL, BIG = 'small', 'big'

    def change_mode(self):
        lg.debug('Changing menu_mode: begin: {}'.format(self.menu_mode))
        if self.menu_mode == CloudSettings.BIG:
            self.menu_mode = CloudSettings.SMALL
        else:
            self.menu_mode = CloudSettings.BIG
        lg.debug('Changing menu_mode: end: {}'.format(self.menu_mode))

    def update_dir(self, dir_, path):
        dir_ = format_name(dir_)
        cur_dir = format_name(path + '/cloud/' + dir_)
        if not os.path.exists(cur_dir):
            fl.abort(404, 'Директория не найдена')
        if dir_ != self.cur_dir_from_user:
            self.current_index = 0
        self.cur_dir_from_user = dir_
        self.current_dir = cur_dir
        self.out_of_root = bool(dir_)
        return self.current_dir


class FileFormatError(Exception):
    pass


class TempUser(UserMixin):
    def __init__(self, dict_):
        if dict_ is None:
            self.exist = False
            return
        elif 'message' in dict_.keys():
            fl.abort(403, dict_['message'])
        self.id = dict_['id']
        self.email = dict_['email']
        self.username = dict_['username']
        self.photo = dict_['photo']
        self.path = dict_['path']
        self.exist = True

    def check_password(self, password):
        res = rq.get(Api.SERVER + '/users/check_password/' + str(self.id),
                     params={'secret_key': Api.KEY,
                             'password': password})
        lg.debug('Result of checking user {}`s password: '.format(self.id) +
                 str(res.json()))
        return res.json()['success']

    def __bool__(self):
        return self.exist


class TempPubl:
    def __init__(self, filename, description, author, show_email=False):
        self.author = author
        self.filename = author.path + '/cloud/' + filename
        self.description = description
        self.show_email = show_email


# Функции сортировки
def get_func(key):
    dict_ = {'alpha': alpha_sorter,
             'time': time_sorter}
    return dict_.get(key, alpha_sorter)


def alpha_sorter(cur_dir, string, reverse=False):
    return sort_func(cur_dir, lambda x: x, string, reverse)


def time_sorter(cur_dir, string, reverse=False):
    return sort_func(cur_dir, lambda f: os.path.getmtime('/'.join([cur_dir,
                                                                   f])),
                     string, reverse)


def sort_func(cur_dir, key_sort, string, reverse=False):
    func = reversed if reverse else return_
    list_ = os.listdir(cur_dir)
    return (list(func(sorted(filter(lambda f: os.path.isdir('/'.join([cur_dir,
                                                                      f])) and
                                    string in f.lower(), list_),
                             key=key_sort))) +
            list(func(sorted(filter(lambda f: os.path.isfile('/'.join([cur_dir,
                                                                       f])) and
                                    string in f.lower(), list_),
                             key=key_sort))))


def return_(arg):
    return arg


# Вспомогательные функции
def format_name(name):
    while '//' in name:
        name = name.replace('//', '/')
    name = name[:-1] if name.endswith('/') else name
    return name


def make_file(dir_, file):
    name = file.filename
    if not name:
        raise FileFormatError('Отсутствует имя файла')
    for char in BAD_CHARS:
        name = name.replace(char, '_')
    dir_ += '/'
    filetype = '.' + name.split('.')[-1]
    new_filename = filename = name[:-len(filetype)]
    i = 2
    while os.path.exists(dir_ + new_filename + filetype):
        new_filename = filename + '_' + str(i)
        i += 1
    file.save(dir_ + new_filename + filetype)


def make_photo(file, user_path):
    type_ = file.filename.split('.')[-1]
    if type_ not in IMAGE_TYPES:
        raise FileFormatError('Неверное расширение фото: {}'.format(type_))
    if not os.path.exists(user_path + '/user_files'):
        os.mkdir(user_path + '/user_files')
    for old in os.listdir(user_path + '/user_files'):
        os.remove(user_path + '/user_files/' + old)
    photoname = user_path + '/user_files/user_photo.' + type_
    file.save(photoname)
    return photoname


def make_publ_file(filename):
    if not os.path.exists(filename):
        fl.abort(404, message='Файл не найден')
    user_dir, name = filename.split('/cloud/')
    name = name.split('/')[-1]
    new_name, ind = name, 2
    while os.path.exists(user_dir + '/public/' + new_name):
        new_name = name.split('.')[-2] + '_' + str(ind) + '.' +\
                   name.split('.')[-1]
        ind += 1
    shutil.copy(filename, user_dir + '/public/' + new_name)
    return user_dir + '/public/' + new_name


def abort_if_no_file(args):
    if not os.path.exists(args.filename):
        fl.abort(404, 'File with path {} isn`t found.'.format(
            args.filename))


# Генерация ключа для формы
def generate_secret_key():
    return ''.join(choices(list(SYMBOLS), k=250))
