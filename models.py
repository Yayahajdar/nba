# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

 
class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    abbr = Column(String, nullable=False)
    name = Column(String, nullable=False)

    players = relationship("Player", back_populates="team")
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    visitor_games = relationship("Game", foreign_keys="Game.visitor_team_id", back_populates="visitor_team")

 
class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    first = Column(String)
    last = Column(String)
    pos = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = relationship("Team", back_populates="players")

 
class Season(Base):
    __tablename__ = "seasons"
    year = Column(Integer, primary_key=True)

 
class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    season = Column(Integer, ForeignKey("seasons.year"))
    date = Column(String)  # نحتفظ بالتاريخ كـ String (يمكن تغييره إلى Date)
    home_team_id = Column(Integer, ForeignKey("teams.id"))
    visitor_team_id = Column(Integer, ForeignKey("teams.id"))
    home_score = Column(Integer, default=0)
    visitor_score = Column(Integer, default=0)

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    visitor_team = relationship("Team", foreign_keys=[visitor_team_id], back_populates="visitor_games")


 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database schema created successfully!")
