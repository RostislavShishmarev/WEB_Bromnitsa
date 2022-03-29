import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase


class File(SqlAlchemyBase):
    __tablename__ = 'files'

    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    path = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)

    users = orm.relation("User", back_populates='file')
