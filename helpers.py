import os
import shutil

IMAGE_TYPES = ('jpg', 'jpeg', 'png', 'svg', 'webp', 'gif', 'ico')


class Errors:
    USER_EXIST = "Такой пользователь уже есть"
    DIFF_PASS = 'Пароли не совпадают'
    NO_USER = "Такого пользователя не существует"
    INCOR_PASS = "Неверный пароль"


class CurrentSettings:
    SMALL, BIG = 'small', 'big'

    def __init__(self):
        self.menu_mode = CurrentSettings.SMALL
        self.out_of_root = False
        self.string = ''
        self.sort_func = alpha_sorter
        self.current_index = 0
        self.files_num = 2

    def change_mode(self):
        if self.menu_mode == CurrentSettings.BIG:
            self.menu_mode = CurrentSettings.SMALL
        else:
            self.menu_mode = CurrentSettings.BIG


class Saver:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def make_publ_file(filename):
    user_dir, name = filename.split('/cloud/')
    new_name, ind = name, 2
    if os.path.exists(user_dir + '/public/' + new_name):
        new_name = name.split('.')[-2] + '_' + str(ind) + '.' +\
                   name.split('.')[-1]
        ind += 1
    shutil.copy(filename, user_dir + '/public/' + new_name)
    return user_dir + '/public/' + new_name


def sort_function(list_, cur_dir):
    key_sort = lambda x: x
    return sorted(list(filter(lambda f: os.path.isdir('/'.join([cur_dir,
                                                                f])), list_)),
                  key=key_sort) +\
           sorted(list(filter(lambda f: os.path.isfile('/'.join([cur_dir,
                                                                 f])), list_)),
                  key=key_sort)


def reverse_dec(sorter):
    def reverser(*args, **kwargs):
        return sorter(*args, **kwargs)[::-1]

    return reverser


def alpha_sorter(list_, cur_dir, string):
    key_sort = lambda x: x
    return sort_func(list_, cur_dir, key_sort, string)


def time_sorter(list_, cur_dir, string):
    key_sort = lambda f: os.path.getmtime('/'.join([cur_dir, f]))
    return sort_func(list_, cur_dir, key_sort, string)


def sort_func(list_, cur_dir, key_sort, string):
    return sorted(list(filter(lambda f: os.path.isdir('/'.join([cur_dir, f]))\
                                        and string in f.lower(), list_)),
                  key=key_sort) +\
           sorted(list(filter(lambda f: os.path.isfile('/'.join([cur_dir, f]))\
                                        and string in f.lower(), list_)),
                  key=key_sort)
