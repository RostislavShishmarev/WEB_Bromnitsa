import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Publication(SqlAlchemyBase):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.String)
    filename = sqlalchemy.Column(sqlalchemy.String)
    show_email = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    author = orm.relation("User")
