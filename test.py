from flask import Flask, render_template, request
import os
from flask import send_from_directory

app = Flask(__name__)
SMALL, BIG = 'small', 'big'


class CurrentSet:
    menu_mode = SMALL


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
def main_page():
    return render_template('TitlePage.html')


@app.route('/cloud', methods=['GET', 'POST'])
@app.route('/cloud/', methods=['GET', 'POST'])
@app.route('/cloud/<path:current_dir>', methods=['GET', 'POST'])
def cloud(current_dir=''):
    current_dir = current_dir.replace('&', '/')
    files = ['../static/users/' + (current_dir + '/' if current_dir else '') + w
             for w in (['..', ] if current_dir else []) + os.listdir('static/users/' + current_dir)]
    if request.method == 'POST':
        if 'change-menu' in request.form.keys():
            CurrentSet.menu_mode = SMALL if CurrentSet.menu_mode == BIG\
                else BIG
        return render_template('Account.html', menu=CurrentSet.menu_mode,
                               files_names=files, os=os)
    return render_template('Account.html', menu=CurrentSet.menu_mode,
                           files_names=files, os=os)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
