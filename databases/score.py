import sqlalchemy

from .db_session import SqlAlchemyBase


class Score(SqlAlchemyBase):
    __tablename__ = "scores"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    game = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    score = sqlalchemy.Column(sqlalchemy.String, nullable=True)
