#!/usr/bin/env python
import os
import sys
import json
import bcrypt

# Ensure root directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.database import SessionLocal
from src.models.deuda import LogSincronizacion, RutaNotificacion, RutaDetalle
from src.models.usuario import Usuario
from src.services.sync_service import SyncService

def run_sync_test():
    print("Iniciando prueba de servicio de sincronización (SyncService)...")
    print("=" * 60)
    
    db = SessionLocal()
    sync = SyncService()
    
    # Asegurar cola local vacía
    sync.limpiar_cola_local()
    
    # Crear un usuario de prueba único para evitar la clave duplicada (id_usuario, fecha_ruta)
    username = "sync_tester_unique"
    existing = db.query(Usuario).filter(Usuario.username == username).first()
    if existing:
        db.delete(existing)
        db.commit()
        
    hashed = bcrypt.hashpw("Password123!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    test_user = Usuario(
        username=username,
        password_hash=hashed,
        nombres="Notificador",
        apellidos="De Pruebas Sync",
        id_rol=3, # NORMAL
        activo=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Usuario de prueba de sync creado con ID {test_user.id_usuario}")
    
    # 1. Probar conectividad online
    is_online = sync.check_online_status()
    print(f"Estado de conectividad inicial: {'ONLINE' if is_online else 'OFFLINE'}")
    
    id_usuario = test_user.id_usuario
    deudas_test = [1] # ID de deuda real existente en la DB
    distancia_km = 3.75
    
    try:
        # 2. Sincronizar una ruta de prueba (Online)
        print("\n[1] Probando sincronización en tiempo real (Online)...")
        res = sync.sincronizar_ruta(id_usuario, len(deudas_test), deudas_test, distancia_km)
        print(f"Resultado: {res}")
        
        if is_online:
            assert res["status"] == "online", "Debió sincronizarse en línea"
            assert "id_ruta" in res, "Debió retornar el ID de la ruta creada"
            
            # Verificar en base de datos
            ruta_db = db.query(RutaNotificacion).filter(RutaNotificacion.id_ruta == res["id_ruta"]).first()
            assert ruta_db is not None, "La ruta no se encontró en la BD"
            assert float(ruta_db.distancia_estimada_km) == distancia_km, "La distancia no coincide"
            
            detalles = db.query(RutaDetalle).filter(RutaDetalle.id_ruta == res["id_ruta"]).all()
            assert len(detalles) == len(deudas_test), "El número de detalles de ruta no coincide"
            
            log = db.query(LogSincronizacion).filter(LogSincronizacion.sync_batch_id == res["batch_id"]).first()
            assert log is not None, "No se registró el log de sincronización en la BD"
            assert log.estado == "EXITOSO", "El estado del log no es EXITOSO"
            
            print("Verificación de base de datos exitosa para sincronización ONLINE!")
            
            # Limpiar datos de prueba
            db.query(RutaDetalle).filter(RutaDetalle.id_ruta == res["id_ruta"]).delete()
            db.delete(ruta_db)
            db.delete(log)
            db.commit()
            print("Limpieza de datos de prueba exitosa.")
        else:
            assert res["status"] == "offline", "Debió encolarse localmente"
            cola = sync.obtener_cola_local()
            assert len(cola["rutas"]) == 1, "La ruta no se guardó en la cola local"
            print("Verificación offline exitosa para encolamiento local!")

        # 3. Simular encolamiento Offline manual
        print("\n[2] Probando encolamiento local y firmado criptográfico (Offline)...")
        sync.encolar_localmente("rutas", {
            "id_usuario": id_usuario,
            "total_deudas": 1,
            "deudas": [1],
            "distancia_km": 1.20,
            "fecha": "2026-05-28"
        })
        
        cola = sync.obtener_cola_local()
        assert len(cola["rutas"]) >= 1, "No se guardó el registro en la cola local"
        print(f"Contenido de cola local: {len(cola['rutas'])} rutas pendientes.")
        
        # 4. Probar procesar_cola_pendiente
        print("\n[3] Probando procesamiento de cola pendiente...")
        proc_res = sync.procesar_cola_pendiente()
        print(f"Resultado procesamiento: {proc_res}")
        
        if is_online:
            assert proc_res["status"] == "success", "Debió procesar con éxito"
            cola_post = sync.obtener_cola_local()
            assert len(cola_post["rutas"]) == 0, "La cola debió quedar vacía tras sincronizar"
            print("Sincronización diferida exitosa y cola limpia!")
            
            # Limpieza en BD de las rutas diferidas
            # Buscar y borrar las rutas de prueba creadas bajo el usuario de prueba
            rutas_diferidas = db.query(RutaNotificacion).filter(RutaNotificacion.id_usuario == id_usuario).all()
            for r in rutas_diferidas:
                db.query(RutaDetalle).filter(RutaDetalle.id_ruta == r.id_ruta).delete()
                db.delete(r)
            db.commit()
            print("Limpieza de rutas diferidas en BD completada.")
        else:
            assert proc_res["status"] == "offline", "Debió permanecer offline"
            print("La cola se mantuvo pendiente correctamente bajo estado offline.")

    finally:
        # Limpieza final
        print("\nLimpiando base de datos y cola local...")
        sync.limpiar_cola_local()
        
        # Asegurar remoción del usuario de pruebas y sus dependencias
        try:
            db.query(RutaDetalle).filter(RutaDetalle.id_ruta.in_(
                db.query(RutaNotificacion.id_ruta).filter(RutaNotificacion.id_usuario == id_usuario)
            )).delete(synchronize_session=False)
            db.query(RutaNotificacion).filter(RutaNotificacion.id_usuario == id_usuario).delete()
            db.delete(test_user)
            db.commit()
            print("Limpieza de usuario y dependencias exitosa.")
        except Exception as e:
            db.rollback()
            print(f"Error de limpieza final: {e}")
        db.close()
        
    print("\n" + "=" * 60)
    print("¡TODAS LAS PRUEBAS DE SINCRONIZACIÓN PASARON CON ÉXITO!")
    print("=" * 60)

if __name__ == "__main__":
    run_sync_test()
