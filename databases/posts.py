import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = "posts"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    anonymously = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    creator = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    group_id = sqlalchemy.Column(sqlalchemy.Integer)
    comments_available = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
