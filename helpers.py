import os
import shutil


class Saver:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


# TEST ><><><><
class Autor:
    id = 1
    name = 'Моккий Кифович'
    photo = 'static/users/1/cloud/User_phoenix.jpg'
    password = 'hoorey!'
    email = 'mokk@mail.ru'
    path = 'static/users/1'
    is_authenticated = True


class flask_login:
    current_user = Autor
# TEST ><><><>< ^


class TempPubl:
    def __init__(self, filename, description, show_email=False,
                 author=flask_login.current_user):
        self.autor = author
        self.filename = flask_login.current_user.path + '/cloud/' + filename
        self.description = description
        self.show_email = show_email


def make_publ_file(name):
    user_dir = flask_login.current_user.path
    filename = user_dir + '/cloud/' + name
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
