from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DateTime, Float

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    type = Column(String)
    description = Column(String)
    amount = Column(Float)

class Statement(Base):
    __tablename__ = "statements"
    id = Column(Integer, primary_key = True)
    name = Column(String)
    type = Column(String)