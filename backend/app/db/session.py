from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..core.config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

def get_db():  # dependency
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()