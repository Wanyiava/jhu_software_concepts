"""Backward-compatible factory import: ``flask --app src.app:create_app``."""
from .flask_app import create_app

__all__ = ["create_app"]
