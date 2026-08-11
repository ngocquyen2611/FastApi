import subprocess
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            cwd=".",
        )
    except FileNotFoundError:
        Base.metadata.create_all(bind=engine)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Database migrations failed") from exc


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()