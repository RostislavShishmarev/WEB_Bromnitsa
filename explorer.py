import os
import shutil


class Explorer:
    def __init__(self, user_path):
        self.boofer = user_path + '/boofer'

    def copy(self, name):
        onlyname = name.split('/')[-1]
        shutil.copy(name, self.boofer + '/' + onlyname)

    def delete(self, name):
        os.remove(name)

    def cut(self, name):
        self.copy(name)
        self.delete(name)

    def get_file(self):
        list_ = os.listdir(self.boofer)


    def paste(self, dirname):
        pass