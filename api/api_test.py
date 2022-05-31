import requests as rq
import unittest as ut

# Работает только с пустой базой данных
ut.TestLoader.sortTestMethodsUsing = None
with open('secret_keys.txt', encoding='utf8') as f:
    KEY = f.read().split('\n')[0]
SERVER = '127.0.0.1:5000'
RQ_USERS_START = 'http://{}/api/users'.format(SERVER)
RQ_PUBLS_START = 'http://{}/api/publications'.format(SERVER)


class Test1UserApi(ut.TestCase):
    def test_01_get_all_users(self):
        res = rq.get(RQ_USERS_START, params={'secret_key': KEY}).json()
        self.assertEqual(res, [])

    def test_02_post_user(self):
        res = rq.post(RQ_USERS_START, params={'secret_key': KEY,
                                              'username': 'Joe',
                                              'email': 'joe@mail.ru',
                                              'password': '123456'}).json()
        self.assertEqual(res, {'success': True})

    def test_03_get_all_users_after_adding(self):
        res = rq.get(RQ_USERS_START, params={'secret_key': KEY}).json()
        del res[0]['password']
        self.assertEqual(res, [{'id': 1,
                                'email': 'joe@mail.ru',
                                'path': 'static/users/1',
                                'photo': 'static/img/No_user.jpg',
                                'username': 'Joe'}])

    def test_03_1_get_user_by_email(self):
        res = rq.get(RQ_USERS_START + '/get_by/email',
                     params={'secret_key': KEY,
                             'email': 'joe@mail.ru'}).json()
        del res['password']
        self.assertEqual(res, {'id': 1,
                               'email': 'joe@mail.ru',
                               'path': 'static/users/1',
                               'photo': 'static/img/No_user.jpg',
                               'username': 'Joe'})

    def test_03_2_get_user_by_path(self):
        res = rq.get(RQ_USERS_START + '/get_by/path',
                     params={'secret_key': KEY,
                             'path': 'static/users/1'}).json()
        del res['password']
        self.assertEqual(res, {'id': 1,
                               'email': 'joe@mail.ru',
                               'path': 'static/users/1',
                               'photo': 'static/img/No_user.jpg',
                               'username': 'Joe'})

    def test_03_3_bad_get_user_by_no_parameter(self):
        res = rq.get(RQ_USERS_START + '/get_by/email',
                     params={'secret_key': KEY,
                             'path': 'static/users/1'})
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(), {'message': 'No parameter email'})

    def test_03_4_bad_get_user_by_wrong_parameter(self):
        res = rq.get(RQ_USERS_START + '/get_by/param',
                     params={'secret_key': KEY,
                             'path': 'static/users/1'})
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'Type param is not email or path'})

    def test_04_get_user(self):
        res = rq.get(RQ_USERS_START + '/1', params={'secret_key': KEY}).json()
        del res['password']
        self.assertEqual(res, {'id': 1,
                               'email': 'joe@mail.ru',
                               'path': 'static/users/1',
                               'photo': 'static/img/No_user.jpg',
                               'username': 'Joe'})

    def test_05_check_right_password(self):
        res = rq.get(RQ_USERS_START + '/check_password/1',
                     params={'secret_key': KEY,
                             'password': '123456'}).json()
        self.assertEqual(res, {'success': True})

    def test_06_check_wrong_password(self):
        res = rq.get(RQ_USERS_START + '/check_password/1', params={
            'secret_key': KEY,
            'password': '1234567'
        }).json()
        self.assertEqual(res, {'success': False})

    def test_07_put_user(self):
        res = rq.put(RQ_USERS_START + '/1', params={
            'secret_key': KEY,
            'password': '1234567',
            'username': 'Donald',
            'email': 'donald@mail.ru',
            'photo': '<path>',
            'path': '<path>'
        }).json()
        self.assertEqual(res, {'success': True})

    def test_08_get_all_users_after_adding(self):
        res = rq.get(RQ_USERS_START, params={'secret_key': KEY}).json()
        del res[0]['password']
        self.assertEqual(res, [{'id': 1,
                                'email': 'donald@mail.ru',
                                'path': '<path>',
                                'photo': '<path>',
                                'username': 'Donald'}])

    def test_09_get_user(self):
        res = rq.get(RQ_USERS_START + '/1', params={'secret_key': KEY}).json()
        del res['password']
        self.assertEqual(res, {'id': 1,
                               'email': 'donald@mail.ru',
                               'path': '<path>',
                               'photo': '<path>',
                               'username': 'Donald'})

    def test_10_check_right_password(self):
        res = rq.get(RQ_USERS_START + '/check_password/1',
                     params={'secret_key': KEY,
                             'password': '1234567'}).json()
        self.assertIn('success', res.keys())
        self.assertEqual(res['success'], True)

    def test_11_check_wrong_password(self):
        res = rq.get(RQ_USERS_START + '/check_password/1', params={
            'secret_key': KEY,
            'password': '123456'
        }).json()
        self.assertEqual(res, {'success': False})

    def test_12_bad_key(self):
        res = rq.get(RQ_USERS_START, params={'secret_key': 'qwerty'})
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(), {'message': 'Wrong secret key'})

    def test_13_bad_post_existing_email(self):
        res = rq.post(RQ_USERS_START, params={
            'secret_key': KEY,
            'password': 'qwertyuiop',
            'username': 'Arseniy',
            'email': 'donald@mail.ru'
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'Email donald@mail.ru already exists'})

    def test_14_0_before(self):
        res = rq.post(RQ_USERS_START, params={
            'secret_key': KEY,
            'password': 'qwertyuiop',
            'username': 'Arseniy',
            'email': 'ars@mail.ru'
        }).json()
        self.assertEqual(res, {'success': True})


class Test2PublApi(ut.TestCase):
    def test_01_get_all_publs(self):
        res = rq.get(RQ_PUBLS_START, params={'secret_key': KEY}).json()
        self.assertEqual(res, [])

    def test_02_post_publ(self):
        res = rq.post(RQ_PUBLS_START, params={'secret_key': KEY,
                                              'description': 'First publ',
                                              'filename': '<path>',
                                              'show_email': True,
                                              'user_id': 1}).json()
        self.assertEqual(res, {'success': True})

    def test_03_get_all_publs_after_adding(self):
        res = rq.get(RQ_PUBLS_START, params={'secret_key': KEY}).json()
        del res[0]['modified_date']
        del res[0]['author']['password']
        self.assertEqual(res, [{'id': 1,
                                'description': 'First publ',
                                'filename': '<path>',
                                'show_email': True,
                                'author': {'id': 1,
                                           'email': 'donald@mail.ru',
                                           'path': '<path>',
                                           'photo': '<path>',
                                           'username': 'Donald'}}])

    def test_04_get_publ(self):
        res = rq.get(RQ_PUBLS_START + '/1', params={'secret_key': KEY}).json()
        del res['modified_date']
        del res['author']['password']
        self.assertEqual(res, {'id': 1,
                               'description': 'First publ',
                               'filename': '<path>',
                               'show_email': True,
                               'author': {'id': 1,
                                          'email': 'donald@mail.ru',
                                          'path': '<path>',
                                          'photo': '<path>',
                                          'username': 'Donald'}})

    def test_05_put_publ(self):
        res = rq.put(RQ_PUBLS_START + '/1', params={
            'secret_key': KEY,
            'description': 'None',
            'filename': '<path2>',
            'show_email': False,
            'user_id': 2
        }).json()
        self.assertEqual(res, {'success': True})

    def test_08_get_all_publs_after_adding(self):
        res = rq.get(RQ_PUBLS_START, params={'secret_key': KEY}).json()
        del res[0]['modified_date']
        del res[0]['author']['password']
        self.assertEqual(res, [{'id': 1,
                                'description': 'None',
                                'filename': '<path2>',
                                'show_email': False,
                                'author': {'id': 2,
                                           'email': 'ars@mail.ru',
                                           'path': 'static/users/2',
                                           'photo': 'static/img/No_user.jpg',
                                           'username': 'Arseniy'}}])

    def test_09_get_publ(self):
        res = rq.get(RQ_PUBLS_START + '/1', params={'secret_key': KEY}).json()
        del res['modified_date']
        del res['author']['password']
        self.assertEqual(res, {'id': 1,
                               'description': 'None',
                               'filename': '<path2>',
                               'show_email': False,
                               'author': {'id': 2,
                                          'email': 'ars@mail.ru',
                                          'path': 'static/users/2',
                                          'photo': 'static/img/No_user.jpg',
                                          'username': 'Arseniy'}})

    def test_12_bad_key(self):
        res = rq.get(RQ_PUBLS_START, params={'secret_key': 'qwerty'})
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(), {'message': 'Wrong secret key'})

    def test_13_bad_post_no_user(self):
        res = rq.post(RQ_PUBLS_START, params={
            'secret_key': KEY,
            'user_id': 3,
            'description': 'None',
            'filename': '<path2>',
            'show_email': False
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'User with id 3 isn`t found'})

    def test_14_bad_put_existing_email(self):
        res = rq.put(RQ_PUBLS_START + '/1', params={
            'secret_key': KEY,
            'user_id': 3
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'User with id 3 isn`t found'})

    def test_15_bad_put_no_id(self):
        res = rq.put(RQ_PUBLS_START + '/2', params={
            'secret_key': KEY,
            'filename': '<path3>'
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'Publication with id 2 isn`t found'})

    def test_15_bad_delete(self):
        res = rq.delete(RQ_PUBLS_START + '/2', params={
            'secret_key': KEY
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'Publication with id 2 isn`t found'})

    def test_16_delete_publ(self):
        res = rq.delete(RQ_PUBLS_START + '/1', params={
            'secret_key': KEY
        }).json()
        self.assertEqual(res, {'success': True})

    def test_17_get_al_publss(self):
        self.test_01_get_all_publs()


class Test3UserApi(ut.TestCase):
    def test_14_1_bad_put_existing_email(self):
        res = rq.put(RQ_USERS_START + '/2', params={
            'secret_key': KEY,
            'password': 'qwertyuiop',
            'username': 'Arseniy',
            'email': 'donald@mail.ru'
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'Email donald@mail.ru already exists'})

    def test_14_2_after(self):
        res = rq.delete(RQ_USERS_START + '/2', params={
            'secret_key': KEY
        }).json()
        self.assertEqual(res, {'success': True})

    def test_15_bad_put_no_id(self):
        res = rq.put(RQ_USERS_START + '/2', params={
            'secret_key': KEY,
            'password': 'qwertyuiop',
            'username': 'Arseniy',
            'email': 'ars@mail.ru'
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(),
                         {'message': 'User with id 2 isn`t found'})

    def test_16_bad_delete(self):
        res = rq.delete(RQ_USERS_START + '/2', params={
            'secret_key': KEY
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(), {'message': 'User with id 2 isn`t found'})

    def test_17_delete_user(self):
        res = rq.delete(RQ_USERS_START + '/1', params={
            'secret_key': KEY
        }).json()
        self.assertEqual(res, {'success': True})

    def test_18_get_al_users(self):
        res = rq.get(RQ_USERS_START, params={'secret_key': KEY}).json()
        self.assertEqual(res, [])


if __name__ == '__main__':
    ut.main()
