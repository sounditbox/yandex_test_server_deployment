from sqlalchemy import Table, Integer, Column, ForeignKey, String
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

association_table = Table(
    'association',
    SqlAlchemyBase.metadata,

    Column('news', Integer, ForeignKey('news.id')),
    Column('category', Integer, ForeignKey('category.id'))
)


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
