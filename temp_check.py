import sys
sys.path.insert(0, r'C:\Users\chara\Pictures\neplatic-desktop')
from src.models.database import SessionLocal
from src.models.usuario import Usuario
from src.models.contribuyente import RolUsuario
db = SessionLocal()
user = db.query(Usuario).filter(Usuario.username == 'admin1', Usuario.activo == True).first()
if user:
    rol = db.query(RolUsuario).filter(RolUsuario.id_rol == user.id_rol).first()
    print(f'Username: {user.username}, Rol codigo: {rol.codigo if rol else None}, Rol nombre: {rol.nombre if rol else None}')
else:
    print('User not found or inactive')
db.close()