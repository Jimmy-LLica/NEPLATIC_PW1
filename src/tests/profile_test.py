import sys
import os
import bcrypt

# Añadir directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import SessionLocal
from src.models.usuario import Usuario
from src.controllers.usuario_controller import UsuarioController

def run_test():
    print("Iniciando prueba de UsuarioController (Perfil y Password)...")
    db = SessionLocal()
    controller = UsuarioController()
    
    # 1. Crear usuario de prueba
    username = "test_profile_user"
    password = "OriginalPassword123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Limpiar si ya existe
    existing = db.query(Usuario).filter(Usuario.username == username).first()
    if existing:
        db.delete(existing)
        db.commit()
        
    test_user = Usuario(
        username=username,
        password_hash=hashed,
        nombres="Original Nombres",
        apellidos="Original Apellidos",
        email="original@example.com",
        telefono="123456789",
        id_rol=3, # NORMAL
        activo=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Usuario de prueba creado con ID {test_user.id_usuario}")
    
    try:
        # 2. Probar obtener_perfil
        print("Probando obtener_perfil...")
        res = controller.obtener_perfil(test_user.id_usuario)
        assert res is not None, "No se pudo obtener el perfil"
        user_db, rol_nombre = res
        assert user_db.username == username, "Nombre de usuario incorrecto"
        assert rol_nombre == "Notificador", f"Rol incorrecto: {rol_nombre}"
        print("Obtención de perfil exitosa! Nombre del rol: Notificador")
        
        # 3. Probar actualizar_perfil
        print("Probando actualizar_perfil...")
        updated = controller.actualizar_perfil(
            test_user.id_usuario,
            nombres="Nuevo Nombre",
            apellidos="Nuevo Apellido",
            email="nuevo@example.com",
            telefono="987654321"
        )
        assert updated is True, "La actualización del perfil falló"
        
        # Verificar en base de datos
        db.refresh(test_user)
        assert test_user.nombres == "Nuevo Nombre", "Nombres no actualizados"
        assert test_user.email == "nuevo@example.com", "Email no actualizado"
        print("Actualización de perfil exitosa en la base de datos!")
        
        # 4. Probar cambiar_contrasena
        print("Probando cambiar_contrasena...")
        
        # 4a. Clave actual incorrecta
        exito, msg = controller.cambiar_contrasena(test_user.id_usuario, "ClaveIncorrecta", "NuevaClave123")
        assert exito is False, "Permitió cambiar clave con la clave actual incorrecta"
        print("Validación de contraseña actual incorrecta funciona correctamente.")
        
        # 4b. Clave nueva inválida (sin mayúscula ni número)
        exito, msg = controller.cambiar_contrasena(test_user.id_usuario, password, "clave")
        assert exito is False, "Permitió cambiar clave por una clave débil"
        print("Validación de complejidad de contraseña débil funciona correctamente.")
        
        # 4c. Cambio exitoso
        nueva_clave = "SecurePassword2026"
        exito, msg = controller.cambiar_contrasena(test_user.id_usuario, password, nueva_clave)
        assert exito is True, f"Error al cambiar contraseña: {msg}"
        
        # Verificar que se puede verificar la contraseña nueva con bcrypt
        db.refresh(test_user)
        assert bcrypt.checkpw(nueva_clave.encode('utf-8'), test_user.password_hash.encode('utf-8')), "La nueva contraseña no coincide con el hash"
        print("Cambio de contraseña exitoso!")
        
        print("\n=========================================")
        print("¡TODAS LAS PRUEBAS DE PERFIL Y CONTRASEÑA PASARON!")
        print("=========================================\n")
    finally:
        # Limpieza
        print("Limpiando base de datos...")
        db.delete(test_user)
        db.commit()
        db.close()
        print("Limpieza completada.")

if __name__ == "__main__":
    run_test()
