import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String,
                                nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True,
                              index=True,
                              unique=True)
    password = sqlalchemy.Column(sqlalchemy.String,
                                        nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String)

    publication = orm.relation("Publication", back_populates='author')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
