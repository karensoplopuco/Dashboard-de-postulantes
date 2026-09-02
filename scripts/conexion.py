"""
conexion.py

Conexión robusta a MongoDB Atlas para el Dashboard de Postulantes.

Características:
- Carga .env desde la raíz del proyecto.
- Valida que existan MONGODB_URI y MONGODB_DB.
- No realiza conexión a MongoDB al importar el módulo.
- Reutiliza un único cliente mediante lru_cache.
- Realiza el ping únicamente cuando se solicita.
- Proporciona mensajes claros ante errores de conexión.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import (
    ServerSelectionTimeoutError,
    ConfigurationError,
    PyMongoError,
)


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

# conexion.py está dentro de:
# Dashboard-de-postulantes/scripts/conexion.py
#
# Por eso parent.parent apunta a:
# Dashboard-de-postulantes/

ROOT = Path(__file__).resolve().parent.parent

ENV_PATH = ROOT / ".env"


# ============================================================
# CARGAR VARIABLES DE ENTORNO
# ============================================================

load_dotenv(dotenv_path=ENV_PATH)


MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
MONGODB_DB = os.getenv("MONGODB_DB", "").strip()


# ============================================================
# VALIDAR CONFIGURACIÓN
# ============================================================

if not MONGODB_URI:
    raise RuntimeError(
        f"No se encontró MONGODB_URI.\n"
        f"Archivo .env esperado en:\n"
        f"{ENV_PATH}"
    )


if not MONGODB_DB:
    raise RuntimeError(
        f"No se encontró MONGODB_DB.\n"
        f"Archivo .env esperado en:\n"
        f"{ENV_PATH}"
    )


# ============================================================
# CLIENTE MONGODB
# ============================================================

@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """
    Crea y reutiliza un único cliente de MongoDB.
    """

    return MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        socketTimeoutMS=20000,
        retryWrites=True,
        appname="DashboardPostulantes",
    )


# ============================================================
# BASE DE DATOS
# ============================================================

def get_db():
    """
    Devuelve la base de datos configurada.

    No realiza una operación de red por sí misma.
    """

    return get_client()[MONGODB_DB]


# ============================================================
# COMPROBAR CONEXIÓN
# ============================================================

def comprobar_conexion() -> bool:
    """
    Comprueba que MongoDB Atlas esté disponible.
    """

    try:

        get_client().admin.command("ping")

        return True

    except ServerSelectionTimeoutError as exc:

        raise ConnectionError(
            "\n"
            "No se pudo conectar con MongoDB Atlas.\n\n"
            "Posibles causas:\n"
            "  1. Tu IP no está permitida en MongoDB Atlas.\n"
            "  2. VPN, firewall o antivirus está bloqueando la conexión.\n"
            "  3. No hay acceso a Internet.\n"
            "  4. MONGODB_URI es incorrecta.\n"
            "  5. El cluster de MongoDB Atlas no está disponible.\n\n"
            "En MongoDB Atlas revisa:\n"
            "Security -> Network Access -> IP Access List.\n\n"
            f"Detalle original:\n{exc}"
        ) from exc

    except ConfigurationError as exc:

        raise ConnectionError(
            "\n"
            "Error en la configuración de MongoDB.\n"
            f"Detalle: {exc}"
        ) from exc

    except PyMongoError as exc:

        raise ConnectionError(
            "\n"
            "Error al conectarse con MongoDB.\n"
            f"Detalle: {exc}"
        ) from exc


# ============================================================
# COMPATIBILIDAD
# ============================================================

# Permite mantener código existente como:
#
# from conexion import db
#
# La creación del objeto NO ejecuta un ping.

db = get_db()