"""
app.py — Backend Flask para sistema de control PID (RPM)
=========================================================
Endpoints:
    POST /api/insert       ← ESP32 envía lectura cada 1s
    GET  /api/latest       ← Interfaz web: indicadores actuales
    GET  /api/data         ← Interfaz web: gráfica últimos 5 min
    GET  /api/setpoint     ← ESP32 lee setpoint al arrancar
    POST /api/setpoint     ← Interfaz web: ajusta setpoint
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from models import db, SensorData, SetpointLog

# ── Setpoint en memoria ───────────────────────────────────────────────────────
# Se inicializa con el valor por defecto al arrancar el servidor.
# El ESP32 lo lee una vez al inicio; la web puede cambiarlo en cualquier momento.
_active_setpoint = None


def get_active_setpoint(app):
    global _active_setpoint
    if _active_setpoint is None:
        _active_setpoint = app.config["DEFAULT_SETPOINT"]
    return _active_setpoint


# ── Fábrica de la app ─────────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
        print(f"[DB] Usando: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # ── Endpoints ─────────────────────────────────────────────────────────────

    @app.route("/api/insert", methods=["POST"])
    def insert():
        """
        El ESP32 llama a este endpoint cada 1 segundo.

        Body JSON esperado:
            { "rpm": 1450.5, "setpoint": 1500.0, "pid_output": 72.3 }

        El backend calcula el error y agrega el timestamp.
        """
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Body JSON requerido"}), 400

        # Validar campos obligatorios
        for field in ("rpm", "setpoint", "pid_output"):
            if field not in data:
                return jsonify({"error": f"Campo faltante: {field}"}), 400

        rpm        = float(data["rpm"])
        sp         = float(data["setpoint"])
        pid_output = float(data["pid_output"])
        error      = round(sp - rpm, 4)

        record = SensorData(
            rpm        = rpm,
            setpoint   = sp,
            error      = error,
            pid_output = pid_output,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({"status": "ok", "id": record.id, "error": error}), 201


    @app.route("/api/latest", methods=["GET"])
    def latest():
        """
        Devuelve el último registro insertado.
        La interfaz web llama esto cada 1s para los indicadores en tiempo real.
        """
        record = SensorData.query.order_by(SensorData.id.desc()).first()
        if not record:
            return jsonify({"status": "sin datos aún"}), 200
        return jsonify(record.to_dict())


    @app.route("/api/data", methods=["GET"])
    def data():
        """
        Devuelve los registros de los últimos 5 minutos.
        La interfaz web llama esto cada 2s para actualizar la gráfica.

        Query param opcional:
            ?minutes=5  (por defecto 5)
        """
        from datetime import datetime, timedelta

        minutes = int(request.args.get("minutes", 5))
        since   = datetime.utcnow() - timedelta(minutes=minutes)

        records = (
            SensorData.query
            .filter(SensorData.timestamp >= since)
            .order_by(SensorData.timestamp.asc())
            .all()
        )
        return jsonify([r.to_dict() for r in records])


    @app.route("/api/setpoint", methods=["GET", "POST"])
    def setpoint():
        """
        GET  → El ESP32 lee el setpoint activo al arrancar.
        POST → La interfaz web cambia el setpoint remotamente.
                Body JSON: { "setpoint": 1600.0 }
        """
        global _active_setpoint

        if request.method == "GET":
            return jsonify({"setpoint": get_active_setpoint(app)})

        # POST
        data = request.get_json(force=True, silent=True)
        if not data or "setpoint" not in data:
            return jsonify({"error": "Campo 'setpoint' requerido"}), 400

        new_sp = float(data["setpoint"])

        # Guardar en memoria y registrar el cambio en BD
        _active_setpoint = new_sp
        log = SetpointLog(setpoint=new_sp, source=data.get("source", "web"))
        db.session.add(log)
        db.session.commit()

        return jsonify({"status": "ok", "setpoint": new_sp})


    @app.route("/api/health", methods=["GET"])
    def health():
        """Endpoint de salud para verificar que el servidor está vivo."""
        return jsonify({"status": "ok"})


    return app


# ── Arranque ──────────────────────────────────────────────────────────────────

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("  Backend PID RPM — corriendo en local")
    print("  http://localhost:5000")
    print("=" * 50)
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
