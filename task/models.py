from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    email = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    sqltime = Column(String(50), nullable=False)


class Website(Base):
    __tablename__ = "Website"

    id = Column(Integer, primary_key=True)
    url = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    failure_count = Column(Integer, Integer(50), nullable=False)
    last_checked = Column(Integer, DateTime(50), nullable=False)

    user = relationship("User", backref="user")
