import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
import datetime


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
    hashed_password = sqlalchemy.Column(sqlalchemy.String,
                                        nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    photo = sqlalchemy.Column(sqlalchemy.String,
                              nullable=True)
    path = sqlalchemy.Column(sqlalchemy.String)

    publication = orm.relation("Publication", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
