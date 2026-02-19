from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/mydatabase"

# Create engine
engine = create_engine(DATABASE_URL)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
