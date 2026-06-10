import sys
sys.path.insert(0, r'C:\Users\chara\Pictures\neplatic-desktop')
from src.models.database import SessionLocal
from src.models.usuario import Usuario
from src.models.contribuyente import RolUsuario
db = SessionLocal()
usernames = ['notificador1', 'notificador2', 'notificador3', 'notificador4', 'supervisor1']
for uname in usernames:
    user = db.query(Usuario).filter(Usuario.username == uname, Usuario.activo == True).first()
    if user:
        rol = db.query(RolUsuario).filter(RolUsuario.id_rol == user.id_rol).first()
        print(f"{uname}: activo={user.activo}, rol_codigo={rol.codigo if rol else None}")
    else:
        print(f"{uname}: no encontrado o inactivo")
db.close()