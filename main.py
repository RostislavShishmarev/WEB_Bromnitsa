import data.db_session as db_session
from data.users import User
from data.publication import Publication

def main():
    db_session.global_init("db/cloud.db")
    user1 = User(
        username='Arty',
        email='test@ts.com',
        photo='C/pho.png',
        path='C/da',

    )
    user1.set_password('123')
    db_sess = db_session.create_session()
    db_sess.add(user1)
    db_sess.commit()


if __name__ == '__main__':
    main()
