"""Expose the FastAPI application to the Vercel Python runtime."""

from backend.main import app


__all__ = ["app"]
