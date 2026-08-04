import os
from collections.abc import Generator
from pathlib import Path
from typing import Mapping

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_PATH = Path(__file__).resolve().parent / "app.db"


def resolve_database_url(
    environment: Mapping[str, str] | None = None,
    *,
    local_database_path: Path = DATABASE_PATH,
    temporary_directory: Path = Path("/tmp"),
) -> str:
    """Return a writable database URL for the active runtime."""
    active_environment = os.environ if environment is None else environment
    configured_url = active_environment.get("DATABASE_URL")
    if configured_url:
        return configured_url

    database_path = (
        temporary_directory / "redesignlife.db"
        if active_environment.get("VERCEL")
        else local_database_path
    )
    return f"sqlite:///{database_path.as_posix()}"


DATABASE_URL = resolve_database_url()

engine_options = (
    {"connect_args": {"check_same_thread": False}}
    if DATABASE_URL.startswith("sqlite:")
    else {}
)
engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
