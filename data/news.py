import datetime

from sqlalchemy import orm, Column, Integer, String, DateTime, Boolean, \
    ForeignKey
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    is_private = Column(Boolean, default=True)
    is_published = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f'<News> {self.id} {self.title} {self.user_id}'
