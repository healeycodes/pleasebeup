from sqlalchemy import Column, Integer, String, ForeignKey
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
    user_id = Column(Integer, ForeignKey('user.id'))
    failure_count = Column(Integer, ForeignKey('person.id'), nullable=False)
    last_checked = Column(Integer, ForeignKey('person.id'), nullable=False)

    user = relationship("User", backref="user")
