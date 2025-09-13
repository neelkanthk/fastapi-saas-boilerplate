from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file if present

# Database configuration
driver = os.getenv("DB_DRIVER")
host = os.getenv("DB_HOST")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")
database_name = os.getenv("DB_NAME")

# Database URL
SQLALCHEMY_DATABASE_URL = f"{driver}://{username}:{password}@{host}:{port}/{database_name}"

# Create SQLAlchemy engine to connect to pgsql
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our application's models
Base = declarative_base()

# Function to get session to the database


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
