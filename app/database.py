from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

# Database connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# Create an engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session 
# SessionLocal creates a new independent session object for each use
# autocommit=False disables automatic commitment -allows for  explicit control over when things are changed
# autoflush=False prevents the session from automatically flushing changes to the db before each query
# bind=engine connects the session to a specific Engine that manages the connection pool
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
class Base(DeclarativeBase):
    pass

# Create a database session (connection) for each request, then automatically closes it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()