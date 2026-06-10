import sys
import os
import bcrypt
from datetime import datetime

# Añadir directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import SessionLocal
from src.models.usuario import Usuario, SesionUsuario
from src.controllers.auth_controller import AuthController

def run_test():
    print("Iniciando prueba de autenticación y logout...")
    db = SessionLocal()
    auth = AuthController()
    
    # 1. Crear un usuario de prueba
    username = "test_user_unique"
    password = "TestPassword123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Limpiar si ya existe de una corrida previa
    existing = db.query(Usuario).filter(Usuario.username == username).first()
    if existing:
        db.query(SesionUsuario).filter(SesionUsuario.id_usuario == existing.id_usuario).delete()
        db.delete(existing)
        db.commit()
        
    test_user = Usuario(
        username=username,
        password_hash=hashed,
        nombres="Usuario",
        apellidos="De Prueba",
        id_rol=3, # NORMAL
        activo=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Usuario de prueba creado con ID {test_user.id_usuario}")
    
    try:
        # 2. Probar Login
        print("Probando AuthController.login...")
        logged_user = auth.login(username, password)
        assert logged_user is not None, "El login falló"
        assert logged_user.username == username, "Usuario incorrecto"
        assert hasattr(logged_user, 'token') and logged_user.token is not None, "El token no fue asignado"
        print(f"Login exitoso! Token generado: {logged_user.token[:30]}...")
        
        # 3. Verificar que la sesión se guardó en la DB
        sesion_db = db.query(SesionUsuario).filter(
            SesionUsuario.id_usuario == logged_user.id_usuario,
            SesionUsuario.activa == True
        ).first()
        assert sesion_db is not None, "La sesión no se registró en la BD"
        assert sesion_db.token == logged_user.token, "El token de la sesión no coincide"
        print("Sesión guardada correctamente en la BD!")
        
        # 4. Probar verify_token
        print("Probando verify_token...")
        verified = auth.verify_token(logged_user.token)
        assert verified is not None, "La verificación del token falló"
        assert verified.username == username, "La verificación retornó el usuario incorrecto"
        print("Verificación de token exitosa!")
        
        # 5. Probar Logout
        print("Probando AuthController.logout...")
        logout_success = auth.logout(logged_user.token)
        assert logout_success is True, "El logout retornó False"
        
        # Verificar que la sesión en DB se desactivó
        db.refresh(sesion_db)
        assert sesion_db.activa is False, "La sesión sigue activa en la BD"
        assert sesion_db.fecha_fin is not None, "La fecha de fin no se registró"
        print("Sesión desactivada correctamente en la BD!")
        
        # 6. Verificar que el token ya no sea válido tras el logout
        print("Probando verify_token con sesión revocada...")
        verified_revoked = auth.verify_token(logged_user.token)
        assert verified_revoked is None, "La verificación del token revocó exitosamente pero retornó un usuario"
        print("Token revocado correctamente rechazado!")
        
        print("\n=========================================")
        print("¡TODAS LAS PRUEBAS DE AUTENTICACIÓN Y LOGOUT PASARON!")
        print("=========================================\n")
    finally:
        # Limpieza
        print("Limpiando base de datos...")
        db.query(SesionUsuario).filter(SesionUsuario.id_usuario == test_user.id_usuario).delete()
        db.delete(test_user)
        db.commit()
        db.close()
        print("Limpieza completada.")

if __name__ == "__main__":
    run_test()
