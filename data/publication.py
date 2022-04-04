import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
import datetime


class Publication(SqlAlchemyBase):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    decription = sqlalchemy.Column(sqlalchemy.String)
    path = sqlalchemy.Column(sqlalchemy.String)
    filename = sqlalchemy.Column(sqlalchemy.String)
    show_email = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    users = orm.relation("User", back_populates='file')
