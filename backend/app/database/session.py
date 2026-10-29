import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger("database")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    try:
        # Test postgresql connection if specified
        if "postgresql" in db_url:
            test_engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL database.")
            return test_engine
    except Exception as e:
        logger.warning(
            f"Could not connect to PostgreSQL ({e}). "
            f"Falling back to local SQLite database at {settings.SQLITE_FALLBACK_URL} for local development."
        )
        db_url = settings.SQLITE_FALLBACK_URL
    
    # SQLite or standard fallback engine
    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    return create_engine(db_url, connect_args=connect_args)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.database import models
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
