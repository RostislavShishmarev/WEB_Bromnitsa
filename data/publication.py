import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Publication(SqlAlchemyBase):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    show_email = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    author = orm.relation("User")
