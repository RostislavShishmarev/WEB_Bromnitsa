import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
import datetime


class File(SqlAlchemyBase):
    __tablename__ = 'files'

    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    path = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    users = orm.relation("User", back_populates='file')
