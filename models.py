import logging
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, 
    DateTime, ForeignKey, Float, Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///schedule_bot.db')
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
    reviews = relationship('Review', back_populates='user')
    points_of_issue = relationship('PointOfIssue', back_populates='owner')


class PointOfIssue(Base):
    __tablename__ = 'points_of_issue'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='points_of_issue')
    rating = Column(Float, default=0.0)
    reviews = relationship('Review', back_populates='point_of_issue')
    shifts = relationship('Shift', back_populates='point')


class Shift(Base):
    __tablename__ = 'shifts'

    id = Column(Integer, primary_key=True)
    point_id = Column(Integer, ForeignKey('points_of_issue.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    worker_id = Column(Integer, ForeignKey('users.id'))
    point = relationship('PointOfIssue', back_populates='shifts')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    point_id = Column(Integer, ForeignKey('points_of_issue.id'), nullable=True)
    rating = Column(Float)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='reviews')
    point_of_issue = relationship('PointOfIssue', back_populates='reviews')


Base.metadata.create_all(engine)

session = Session()
