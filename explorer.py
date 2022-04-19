import os
import shutil
import datetime


class Explorer:
    def __init__(self, user):
        if user and user.is_authenticated:
            self.boofer = user.path + '/boofer'
        else:
            self.boofer = None

    def copy(self, name):
        if not self.boofer:
            return False
        onlyname = name.split('/')[-1]
        try:
            self.clean_boofer()
            if os.path.isdir(name):
                shutil.copytree(name, self.boofer + '/' + onlyname)
            else:
                shutil.copy(name, self.boofer + '/' + onlyname)
        except Exception as ex:
             return self.make_error('copy', ex)
        return True

    def delete(self, name):
        try:
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                os.remove(name)
        except Exception as ex:
            return self.make_error('deletion', ex)
        return True

    def cut(self, name):
        self.copy(name)
        self.delete(name)
        return True

    def paste(self, dirname):
        old = self.get_file_name()
        if not old or not self.boofer:
            return False
        new = dirname + '/' + old.split('/')[-1]
        try:
            shutil.copy(old, new)
        except Exception as ex:
            return self.make_error('pasting', ex)
        return True

    def get_file_name(self):
        list_ = os.listdir(self.boofer)
        return None if not list_ else list_[0]

    def make_error(self, where, ex):
        if not os.path.exists('logs'):
            os.mkdir('logs')
        with open(self.get_error().format(where), mode='w',
                  encoding='utf8') as f:
            f.write(str(ex))
        return False

    def get_error(self):
        return datetime.datetime.now().strftime('logs/%H_%M_%S-%d_%m_%Y_\
_{}_error.txt')

    def clean_boofer(self):
        for name in os.listdir(self.boofer):
            self.delete(self.boofer + '/' + name)
