"""
models.py — Definición de tablas con SQLAlchemy
================================================
Compatible con SQLite (local) y PostgreSQL (Railway).
El cambio entre ambas se hace únicamente en config.py.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SensorData(db.Model):
    """
    Registro principal de trazabilidad.
    El ESP32 inserta una fila cada segundo.
    """
    __tablename__ = "sensor_data"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    rpm        = db.Column(db.Float, nullable=False)   # Variable controlada (PV)
    setpoint   = db.Column(db.Float, nullable=False)   # Punto de consigna (SP)
    error      = db.Column(db.Float, nullable=False)   # SP - PV  (calculado en backend)
    pid_output = db.Column(db.Float, nullable=False)   # Salida del controlador (0–100 %)

    def to_dict(self):
        return {
            "id":         self.id,
            "timestamp":  self.timestamp.isoformat(),
            "rpm":        self.rpm,
            "setpoint":   self.setpoint,
            "error":      self.error,
            "pid_output": self.pid_output,
        }


class SetpointLog(db.Model):
    """
    Historial de cambios de setpoint hechos desde la interfaz web.
    Permite saber quién cambió qué y cuándo.
    """
    __tablename__ = "setpoint_log"

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    setpoint  = db.Column(db.Float, nullable=False)
    source    = db.Column(db.String(50), default="web")  # 'web' | 'api' | 'esp32'

    def to_dict(self):
        return {
            "id":        self.id,
            "timestamp": self.timestamp.isoformat(),
            "setpoint":  self.setpoint,
            "source":    self.source,
        }
