from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, session

#allow multiple threads
engine = create_engine("sqlite:///vehicles.db", connect_args={"check_same_thread": False})

#control when change are committed
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

"""
-Open new database session connection and closes it after to prevent leaks 
"""
def get_db():
    with SessionLocal() as db:
        yield db



