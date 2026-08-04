import builtins
import importlib
import sys
from pathlib import Path

from backend import database


def test_serverless_app_import_does_not_require_uvicorn(monkeypatch) -> None:
    """The Vercel entrypoint loads without the local development server package."""
    real_import = builtins.__import__

    def import_without_uvicorn(name, *args, **kwargs):
        if name == "uvicorn":
            raise ModuleNotFoundError("uvicorn is not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_uvicorn)
    sys.modules.pop("backend.main", None)

    imported_main = importlib.import_module("backend.main")

    assert imported_main.app.title == "Redesign Life API"


def test_vercel_uses_writable_temporary_sqlite_path() -> None:
    """Vercel functions keep SQLite writes out of the read-only source bundle."""
    database_url = database.resolve_database_url(
        {"VERCEL": "1"},
        local_database_path=Path("C:/project/backend/app.db"),
        temporary_directory=Path("C:/tmp"),
    )

    assert database_url == "sqlite:///C:/tmp/redesignlife.db"


def test_explicit_database_url_overrides_platform_defaults() -> None:
    """A managed database connection takes precedence over local storage."""
    database_url = database.resolve_database_url(
        {
            "VERCEL": "1",
            "DATABASE_URL": "postgresql+psycopg://example.invalid/redesignlife",
        },
        local_database_path=Path("C:/project/backend/app.db"),
        temporary_directory=Path("C:/tmp"),
    )

    assert database_url == "postgresql+psycopg://example.invalid/redesignlife"
