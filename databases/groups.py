import sqlalchemy

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = "groups"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    admins_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)
