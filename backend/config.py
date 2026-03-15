"""
config.py — Configuración del entorno
======================================
En local:   usa SQLite automáticamente (no requiere instalación).
En Railway: lee la variable DATABASE_URL que Railway inyecta solo.

Uso:
    En local no necesitas hacer nada extra.
    En Railway defines las variables de entorno desde su dashboard.
"""

import os


class Config:
    # ── Base de datos ──────────────────────────────────────────────────────────
    # Railway inyecta DATABASE_URL automáticamente cuando añades PostgreSQL.
    # Si esa variable no existe (local), cae a SQLite.
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///pid_control.db")

    # Railway usa el prefijo "postgres://" (obsoleto en SQLAlchemy 1.4+).
    # Esta línea lo corrige a "postgresql://" si hace falta.
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI          = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS   = False

    # ── Setpoint por defecto ───────────────────────────────────────────────────
    # El ESP32 lo leerá al arrancar desde GET /api/setpoint.
    DEFAULT_SETPOINT = float(os.environ.get("DEFAULT_SETPOINT", 1500.0))  # RPM

    # ── CORS ───────────────────────────────────────────────────────────────────
    # En local acepta cualquier origen. En Railway puedes restringirlo
    # a la URL de tu GitHub Pages si quieres mayor seguridad.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # ── Flask ──────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-cambiar-en-produccion")
    DEBUG      = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
