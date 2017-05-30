"""
Nathan Hernandez
Udacity FullStack NanoDegree
Database Schema/Models
    -ver 0.2 - 05/30/17 (PostgreSQL version)
    -ver 0.1 - 05/2017
"""

import sys
import datetime
import getpass

from collections import OrderedDict

from sqlalchemy import (Column, ForeignKey, Integer, String, Text,
                        DateTime, Enum, UniqueConstraint, create_engine)
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from sqlalchemy.schema import Table

DATABASE = {
    'drivername': 'postgres',
    'host': '',
    'port': '5432',
    'username': '%s' % getpass.getuser(), 
    'password': '',
    'database': 'udacity_catalog'
}

Base = declarative_base()


"""
Serializer Class
"""


class SerializableOrdered(object):
    # SerializableOrdered class based off of example using OrderedDict
    # found here: http://piotr.banaszkiewicz.org/blog/2012/06/30
    # /serialize-sqlalchemy-results-into-json/
    # Returns data in serializable format
    def _asdict(self):
        my_dict = OrderedDict()
        for key in self.__mapper__.columns.keys():
            my_dict[key] = getattr(self, key)
        # print my_dict
        return my_dict


"""
Schema Models
"""


class LoginType(Base, SerializableOrdered):
    # Initial allowable login value is only "Google"
    # Can expand this enum type later (e.g. Facebook, LinkedIn, etc...)
    __tablename__ = 'logintype'
    id = Column(Integer, primary_key=True)
    source = Column(String(40), nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base, SerializableOrdered):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    created_by = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_update_by = Column(Integer, ForeignKey('user.id'))
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("Item", order_by="Item.id",
                         backref=backref("category", lazy="joined"))


class Item(Base, SerializableOrdered):
    __tablename__ = 'item'
    # explicit/composite unique constraint
    __table_args__ = (
        UniqueConstraint('category_id', 'name', name='categ_itemname'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)

    created_by = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_update_by = Column(Integer, ForeignKey('user.id'))
    updated = Column(DateTime(timezone=True), onupdate=func.now())

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    # category = relationship("Category")


"""
User/Role specific Models
"""


# User/Role Association used in USER table below
user_role_association = Table('user_role_association', Base.metadata,
                              Column('user_id', Integer(),
                                     ForeignKey('user.id'),
                                     primary_key=True),
                              Column('role_id', Integer(),
                                     ForeignKey('role.id'),
                                     primary_key=True))


class User(Base, SerializableOrdered):
    __tablename__ = 'user'
    # explicit/composite unique constraint
    __table_args__ = (
        UniqueConstraint('email', 'logintype_id', name='email_logintype'),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    picture = Column(String(256))
    email = Column(String(256), nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now())

    roles = relationship("Role", secondary='user_role_association',
                         order_by="Role.id")

    logintype_id = Column(Integer, ForeignKey('logintype.id'), nullable=False)
    logintype = relationship("LoginType")


class Role(Base, SerializableOrdered):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    permission = Column(String(40), nullable=False, unique=True)

    users = relationship("User", secondary='user_role_association',
                         order_by="User.id")


engine = create_engine(URL(**DATABASE))
Base.metadata.create_all(engine)
