import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Cutoff(Base):
    __tablename__ = "cutoffs"

    id = Column(Integer, primary_key=True)
    college_name = Column(String)
    branch_name = Column(String)
    category = Column(String)
    cap_round = Column(Integer)
    percentile = Column(Float)
    city = Column(String)

# Get the folder where database.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Make sure the data folder exists (creates it if missing)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Build the full path to the database file
DB_PATH = os.path.join(DATA_DIR, "cutoffs.db")

# Convert backslashes to forward slashes (required for Windows + SQLite)
DB_URL = "sqlite:///" + DB_PATH.replace("\\", "/")

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)