import os
import shutil
from flask_restful import abort

IMAGE_TYPES = ('jpg', 'jpeg', 'png', 'svg', 'webp', 'gif', 'ico')
BAD_CHARS = {' ', '/', '\\', '&', '?', '@', '"', "'", '(', ')'}
DEFAULT_PHOTO = 'static/img/No_user.jpg'


class Errors:
    USER_EXIST = "Такой пользователь уже есть"
    DIFF_PASS = 'Пароли не совпадают'
    NO_USER = "Такого пользователя не существует"
    INCOR_PASS = "Неверный пароль"
    DIR_EXIST = "Такая директория уже есть"
    FILE_EXISTS = "Такой файл уже есть."
    BAD_CHAR = "Встречаются недопустимые символы: "
    BAD_FORMAT = "Некорректный формат файла."


class CurrentSettings:
    SMALL, BIG = 'small', 'big'

    def __init__(self):
        self.current_dir = ''
        self.cur_dir_from_user = ''
        self.menu_mode = CurrentSettings.SMALL
        self.out_of_root = False
        self.string = ''
        self.sort_func = alpha_sorter
        self.reverse_files = False
        self.current_index = 0
        self.files_num = 10

    def change_mode(self):
        if self.menu_mode == CurrentSettings.BIG:
            self.menu_mode = CurrentSettings.SMALL
        else:
            self.menu_mode = CurrentSettings.BIG

    def update_dir(self, dir_, path):
        dir_ = format_name(dir_)
        cur_dir = format_name(path + '/cloud/' + dir_)
        if not os.path.exists(cur_dir):
            abort(404, message='Директория не найдена')
        if dir_ != self.cur_dir_from_user:
            self.current_index = 0
        self.cur_dir_from_user = dir_
        self.current_dir = cur_dir
        self.out_of_root = bool(dir_)
        return self.current_dir


class Saver:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def alpha_sorter(cur_dir, string, reverse=False):
    return sort_func(cur_dir, lambda x: x, string, reverse)


def time_sorter(cur_dir, string, reverse=False):
    return sort_func(cur_dir, lambda f: os.path.getmtime('/'.join([cur_dir,
                                                                   f])),
                     string, reverse)


def sort_func(cur_dir, key_sort, string, reverse=False):
    func = reversed if reverse else return_
    list_ = os.listdir(cur_dir)
    return list(func(sorted(filter(lambda f: os.path.isdir('/'.join([cur_dir,
                                                                     f]))\
                                             and string in f.lower(), list_),
                       key=key_sort))) +\
           list(func(sorted(filter(lambda f: os.path.isfile('/'.join([cur_dir,
                                                                      f]))\
                                             and string in f.lower(), list_),
                       key=key_sort)))


def return_(arg):
    return arg


def format_name(name):
    while '//' in name:
        name = name.replace('//', '/')
    name = name[:-1] if name.endswith('/') else name
    return name


def make_file(dir_, file):
    name = file.filename
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
        return None
    if not os.path.exists(user_path + '/user_files'):
        os.mkdir(user_path + '/user_files')
    for old in os.listdir(user_path + '/user_files'):
        os.remove(user_path + '/user_files/' + old)
    photoname = user_path + '/user_files/user_photo.' + type_
    file.save(photoname)
    return photoname


def make_publ_file(filename):
    if not os.path.exists(filename):
        abort(404, message='Файл не найден')
    user_dir, name = filename.split('/cloud/')
    name = name.split('/')[-1]
    new_name, ind = name, 2
    while os.path.exists(user_dir + '/public/' + new_name):
        new_name = name.split('.')[-2] + '_' + str(ind) + '.' +\
                   name.split('.')[-1]
        ind += 1
    shutil.copy(filename, user_dir + '/public/' + new_name)
    return user_dir + '/public/' + new_name
