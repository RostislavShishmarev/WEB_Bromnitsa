import requests as rq
import unittest as ut

ut.TestLoader.sortTestMethodsUsing = None
with open('secret_keys.txt', encoding='utf8') as f:
    KEY = f.read().split('\n')[0]
RQ_USERS_START = 'http://127.0.0.1:5000/api/users'


class TestUserApi(ut.TestCase):
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

    def test_15_bad_delete(self):
        res = rq.delete(RQ_USERS_START + '/2', params={
            'secret_key': KEY
        })
        self.assertEqual(res.ok, False)
        self.assertEqual(res.json(), {'message': 'User with id 2 isn`t found'})

    def test_16_delete_user(self):
        res = rq.delete(RQ_USERS_START + '/1', params={
            'secret_key': KEY
        }).json()
        self.assertEqual(res, {'success': True})

    def test_17_get_al_users(self):
        self.test_01_get_all_users()


if __name__ == '__main__':
    ut.main()
