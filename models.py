import logging
from sqlalchemy import (
    create_engine, Column, Integer, String, 
    ForeignKey, Float, Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///bot.db')
Session = sessionmaker(bind=engine)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    role = Column(String)
    rating = Column(Float, default=0.0)
    points = relationship('Point', back_populates='owner')


class Point(Base):
    __tablename__ = 'points'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='points')
    rating = Column(Float, default=0.0)
    shifts = relationship('Shift', back_populates='point')


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    point_id = Column(Integer, ForeignKey('points.id'))
    date = Column(Date, nullable=False)
    worker_id = Column(Integer, ForeignKey('users.id'))
    point = relationship('Point', back_populates='shifts')


Base.metadata.create_all(engine)

session = Session()
