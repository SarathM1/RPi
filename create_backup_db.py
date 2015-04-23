import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class dieselLevel(Base):
    __tablename__ = 'dieselLevel'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    device = Column(String(25))
    level = Column(Integer)
    mTime = Column(String(30),unique=True)

engine = create_engine('sqlite:///sqlalchemy_example.db')

Base.metadata.create_all(engine)