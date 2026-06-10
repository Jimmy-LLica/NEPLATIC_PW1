#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.models.database import engine, Base
from src.models.usuario import Usuario, Contribuyente
from src.models.contribuyente import Sector, Manzana, Lote, Via
from src.models.deuda import Deuda, Notificacion, RutaNotificacion

print("Neplatic Desktop - Test Database Connection")
print("=" * 50)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"PostgreSQL connection: OK")
        print(f"Version: {result.scalar()}")
    print("All models loaded successfully")
    print("Schema 'neplatic' configured")
except Exception as e:
    print(f"Connection error: {e}")