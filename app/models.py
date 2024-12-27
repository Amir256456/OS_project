from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

# Enums
class Gender(PyEnum):
    Male = "Male"
    Female = "Female"

class GameStatus(PyEnum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"

class GameType(PyEnum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"

class Role(PyEnum):
    MANAGER = "MANAGER"
    MINER = "MINER"
    WARRIOR = "WARRIOR"

class Team(PyEnum):
    TEAM1 = "TEAM1"
    TEAM2 = "TEAM2"

class GameResult(PyEnum):
    WIN = "WIN"
    LOSE = "LOSE"

# Tables
class Icon(Base):
    __tablename__ = 'icons'
    icon_id = Column(Integer, primary_key=True, autoincrement=True)
    icon_name = Column(String(20), nullable=False)

class Achievement(Base):
    __tablename__ = 'achievements'
    achieve_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # Updated to varchar(50) from varchar(20)
    description = Column(String(255))  # Updated to varchar(255)

class Player(Base):
    __tablename__ = 'player'
    username = Column(String(20), primary_key=True)
    name = Column(String(20), nullable=False)
    surename = Column(String(20))
    gender = Column(Enum(Gender), nullable=True)
    b_date = Column(Date)
    age = Column(Integer)
    address = Column(String(100))
    email = Column(String(50))
    password = Column(CHAR(255), nullable=False)  # Updated length to 255 for hashed password
    icon_id = Column(Integer, ForeignKey('icons.icon_id'))

    # Relationships
    icon = relationship('Icon', backref='players')

class Game(Base):
    __tablename__ = 'game'
    match_id = Column(String(50), primary_key=True)  # Updated length to varchar(50)
    status = Column(Enum(GameStatus), nullable=False)
    game_pass = Column(CHAR(32), nullable=True)  # Storing MD5 hash
    game_type = Column(Enum(GameType), nullable=False)

class Achieves(Base):
    __tablename__ = 'achieves'
    username = Column(String(20), ForeignKey('player.username'), primary_key=True)
    achieve_id = Column(Integer, ForeignKey('achievements.achieve_id'), primary_key=True)

    # Relationships
    player = relationship('Player', backref='achievements')
    achievement = relationship('Achievement', backref='players')

class Plays(Base):
    __tablename__ = 'plays'
    username = Column(String(20), ForeignKey('player.username'), primary_key=True)
    match_id = Column(String(50), ForeignKey('game.match_id'), primary_key=True)  # Updated length to varchar(50)
    team = Column(Enum(Team), nullable=True)
    role1 = Column(Enum(Role), nullable=True)
    role2 = Column(Enum(Role), nullable=True)
    role3 = Column(Enum(Role), nullable=True)
    win_or_lose = Column(Enum(GameResult), nullable=True)

    # Relationships
    player = relationship('Player', backref='games')
    game = relationship('Game', backref='players')


