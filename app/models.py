from sqlalchemy import Column, String, Integer, Date, Enum, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

# Enum for gender
class Gender(PyEnum):
    Male = "Male"
    Female = "Female"

# Enum for game status
class GameStatus(PyEnum):
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"

# Enum for game type
class GameType(PyEnum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"

# Enum for roles
class Role(PyEnum):
    MANAGER = "MANAGER"
    MINER = "MINER"
    WARRIOR = "WARRIOR"

# Enum for teams
class Team(PyEnum):
    TEAM1 = 'TEAM1'
    TEAM2 = 'TEAM2'

class GameResult(PyEnum):
    WIN = 'WIN'
    Lose = 'LOSE'

# Table: icons
class Icon(Base):
    __tablename__ = 'icons'
    icon_id = Column(Integer, primary_key=True, autoincrement=True)
    icon_name = Column(String(20), nullable=False)


# Table: achievements
class Achievement(Base):
    __tablename__ = 'achievements'
    achieve_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    description = Column(String(200))


# Table: player
class Player(Base):
    __tablename__ = 'player'
    username = Column(String(20), primary_key=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20))
    gender = Column(Enum(Gender), nullable=True)
    b_date = Column(Date)
    age = Column(Integer)
    address = Column(String(100))
    email = Column(String(50))
    password = Column(CHAR(32), nullable=False)  # MD5 hash
    icon_id = Column(Integer, ForeignKey('icons.icon_id'))

    # Relationships
    icon = relationship('Icon', backref='players')


# Table: game
class Game(Base):
    __tablename__ = 'game'
    game_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(Enum(GameStatus), nullable=False)
    game_pass = Column(CHAR(32), nullable=False)  # MD5 hash
    game_type = Column(Enum(GameType), nullable=False)




# Association Table: achieves
class Achieves(Base):
    __tablename__ = 'achieves'
    username = Column(String(20), ForeignKey('player.username'), primary_key=True)
    achieve_id = Column(Integer, ForeignKey('achievements.achieve_id'), primary_key=True)

    # Relationships
    player = relationship('Player', backref='achievements')
    achievement = relationship('Achievement', backref='players')


# Association Table: plays
class Plays(Base):
    __tablename__ = 'plays'
    username = Column(String(20), ForeignKey('player.username'), primary_key=True)
    game_id = Column(Integer, ForeignKey('game.game_id'), primary_key=True)
    team = Column(Enum(Team))
    role1 = Column(Enum(Role))
    role2 = Column(Enum(Role))
    role3 = Column(Enum(Role))
    win_or_lose = Column(Enum(GameResult))

    # Relationships
    player = relationship('Player', backref='games')
    game = relationship('Game', backref='players')
