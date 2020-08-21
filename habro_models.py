from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

"""
one to many - один к многому -> many to one
many to many - многое к многому
one to one - один к одному
"""

tag_post = Table('tag_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id'))
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='post')
    tag = relationship('Tag', secondary=tag_post, back_populates='post')

    def __init__(self, title: str, url: str, writer, tags: list = None):
        self.title = title
        self.url = url
        self.writer = writer
        if tags:
            self.tag.extend(tags)


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    post = relationship("Post", back_populates='writer')

    def __init__(self, name, url, username):
        self.name = name
        self.url = url
        self.username = username


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=tag_post, back_populates='tag')

    def __init__(self, name, url):
        self.name = name
        self.url = url
