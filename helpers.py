import os
import shutil

IMAGE_TYPES = ('jpg', 'jpeg', 'png', 'svg', 'webp', 'gif', 'ico')
BAD_CHARS = {' ', '/', '\\', '&', '?', '@', '"', "'", '(', ')'}


class Errors:
    USER_EXIST = "Такой пользователь уже есть"
    DIFF_PASS = 'Пароли не совпадают'
    NO_USER = "Такого пользователя не существует"
    INCOR_PASS = "Неверный пароль"
    DIR_EXIST = "Такая директория уже есть"
    FILE_EXISTS = "Такой файл уже есть."
    BAD_CHAR = "Встречаются недопустимые символы: "


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
        self.files_num = 12

    def change_mode(self):
        if self.menu_mode == CurrentSettings.BIG:
            self.menu_mode = CurrentSettings.SMALL
        else:
            self.menu_mode = CurrentSettings.BIG

    def update_dir(self, dir_, path):
        self.cur_dir_from_user = dir_
        self.current_dir = format_name(path + '/cloud/' + dir_)
        self.out_of_root = bool(dir_)
        return self.current_dir


class Saver:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def make_publ_file(filename):
    user_dir, name = filename.split('/cloud/')
    name = name.split('/')[-1]
    new_name, ind = name, 2
    if os.path.exists(user_dir + '/public/' + new_name):
        new_name = name.split('.')[-2] + '_' + str(ind) + '.' +\
                   name.split('.')[-1]
        ind += 1
    shutil.copy(filename, user_dir + '/public/' + new_name)
    return user_dir + '/public/' + new_name


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


def format_name(name):
    while '//' in name:
        name = name.replace('//', '/')
    name = name[:-1] if name.endswith('/') else name
    return name


def return_(arg):
    return arg

def make_file(dir_, file):
    name = file.filename
    for char in BAD_CHARS:
        name = name.replace(char, '_')
    filename = '/' + name
    filetype = filename.split('.')[-1]
    filename = filename[:-len(filetype)]
    i = 0
    while os.path.exists(dir_ + filename):
        filename = filename + '_' + str(i)
        i += 1
    file.save(dir_ + filename + '.' + filetype)
