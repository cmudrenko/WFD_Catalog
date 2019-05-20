import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

# Builds a column in the table to accept a user


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

# Builds a column in the table to accept the days of the week


class Days(Base):
    __tablename__ = 'days'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }

# Builds a column in the table to accept different meals


class MealOption(Base):
    __tablename__ = 'meal_option'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    ingredients = Column(String(250))
    days_id = Column(Integer, ForeignKey('days.id'))
    days = relationship("Days", backref=backref("meal_options", cascade="all, delete"))
    #days = relationship(Days, single_parent=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'ingredients': self.ingredients,
            'id': self.id,
        }

engine = create_engine('sqlite:///whatsfordinner.db')


Base.metadata.create_all(engine)
