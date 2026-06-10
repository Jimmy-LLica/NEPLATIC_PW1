import os
import sys
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.update({
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "neplatic",
    "DB_USER": "postgres",
    "DB_PASSWORD": "postgres",
    "DB_SCHEMA": "neplatic"
})

from src.models.database import engine
from src.utils.logger import setup_logger

logger = setup_logger("neplatic-desktop")

print("Neplatic Desktop - Verificacion de Configuracion")
print("=" * 50)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Conexion a base de datos: OK")
except Exception as e:
    print(f"Error de conexion: {e}")

