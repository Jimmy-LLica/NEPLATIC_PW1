"""
Script para insertar datos de prueba para notificacion de visita.
Ejecutar: py seed_test_notificacion.py
"""
import sys
import os
import bcrypt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.database import SessionLocal
from src.models.usuario import Usuario
from src.models.contribuyente import (
    RolUsuario, Permiso, RolPermiso, EstadoNotificacion,
    TipoTributo, EstadoCobranza, TipoDocumento,
    Sector, Manzana, Via, Lote, Contribuyente,
)
from src.models.deuda import Deuda, RutaNotificacion, RutaDetalle, ContribuyenteLote


def seed():
    db = SessionLocal()

    try:
        # ---------- CATALOGOS ----------
        roles = [
            RolUsuario(id_rol=1, codigo="ADMIN", nombre="Administrador", activo=True),
            RolUsuario(id_rol=2, codigo="SUPERVISOR", nombre="Supervisor", activo=True),
            RolUsuario(id_rol=3, codigo="NORMAL", nombre="Notificador", activo=True),
        ]
        for r in roles:
            existing = db.query(RolUsuario).filter(RolUsuario.id_rol == r.id_rol).first()
            if not existing:
                db.add(r)

        estados_notif = [
            EstadoNotificacion(id_estado_notif=1, codigo="NOTIFICADO", nombre="Notificado", color_hex="#16a34a"),
            EstadoNotificacion(id_estado_notif=2, codigo="AUSENTE", nombre="Ausente", color_hex="#f59e0b"),
            EstadoNotificacion(id_estado_notif=3, codigo="DIR_ERRADA", nombre="Direccion errada", color_hex="#dc2626"),
            EstadoNotificacion(id_estado_notif=4, codigo="RECHAZADO", nombre="Rechazado", color_hex="#7c3aed"),
            EstadoNotificacion(id_estado_notif=5, codigo="FALLECIDO", nombre="Fallecido", color_hex="#6b7280"),
        ]
        for e in estados_notif:
            existing = db.query(EstadoNotificacion).filter(EstadoNotificacion.id_estado_notif == e.id_estado_notif).first()
            if not existing:
                db.add(e)

        tributos = [
            TipoTributo(id_tipo_tributo=1, codigo="PREDIAL", nombre="Impuesto Predial", activo=True),
            TipoTributo(id_tipo_tributo=2, codigo="ARBITRIOS", nombre="Arbitrios Municipales", activo=True),
        ]
        for t in tributos:
            existing = db.query(TipoTributo).filter(TipoTributo.id_tipo_tributo == t.id_tipo_tributo).first()
            if not existing:
                db.add(t)

        cobranzas = [
            EstadoCobranza(id_estado=1, codigo="SIN_PROCESO", nombre="Sin proceso", color_hex="#3b82f6", prioridad=1, activo=True),
            EstadoCobranza(id_estado=2, codigo="ORDINARIA", nombre="Ordinaria", color_hex="#7c2d12", prioridad=2, activo=True),
            EstadoCobranza(id_estado=3, codigo="COACTIVA", nombre="Coactiva", color_hex="#dc2626", prioridad=3, activo=True),
        ]
        for c in cobranzas:
            existing = db.query(EstadoCobranza).filter(EstadoCobranza.id_estado == c.id_estado).first()
            if not existing:
                db.add(c)

        docs = [
            TipoDocumento(id_tipo_doc=1, codigo="D", nombre="DNI", activo=True),
            TipoDocumento(id_tipo_doc=2, codigo="R", nombre="RUC", activo=True),
        ]
        for d in docs:
            existing = db.query(TipoDocumento).filter(TipoDocumento.id_tipo_doc == d.id_tipo_doc).first()
            if not existing:
                db.add(d)

        db.commit()

        # ---------- GEO ----------
        sector = db.query(Sector).filter(Sector.id_sector == 1).first()
        if not sector:
            sector = Sector(id_sector=1, codigo="S01", nombre="Sector Centro", activo=True)
            db.add(sector)
            db.commit()

        manzana = db.query(Manzana).filter(Manzana.id_manzana == 1).first()
        if not manzana:
            manzana = Manzana(id_manzana=1, id_sector=1, codigo="MZ-001", activo=True)
            db.add(manzana)
            db.commit()

        via = db.query(Via).filter(Via.id_via == 1).first()
        if not via:
            via = Via(id_via=1, codigo="V-001", nombre="Av. Principal", tipo="AVENIDA")
            db.add(via)
            db.commit()

        lotes_data = [
            Lote(id_lote=1, id_manzana=1, id_via=1, codigo="L-001", numero_municipal="100", direccion="Av. Principal 100", activo=True),
            Lote(id_lote=2, id_manzana=1, id_via=1, codigo="L-002", numero_municipal="200", direccion="Av. Principal 200", activo=True),
            Lote(id_lote=3, id_manzana=1, id_via=1, codigo="L-003", numero_municipal="300", direccion="Calle Secundaria 50", activo=True),
        ]
        for l in lotes_data:
            existing = db.query(Lote).filter(Lote.id_lote == l.id_lote).first()
            if not existing:
                db.add(l)
        db.commit()

        # ---------- CONTRIBUYENTES ----------
        contribs = [
            Contribuyente(id_contribuyente=1, id_tipo_doc=1, numero_documento="12345678", nombres="Juan", apellido_paterno="Perez", apellido_materno="Garcia", direccion_fiscal="Av. Principal 100", activo=True),
            Contribuyente(id_contribuyente=2, id_tipo_doc=1, numero_documento="87654321", nombres="Maria", apellido_paterno="Lopez", apellido_materno="Quispe", direccion_fiscal="Av. Principal 200", activo=True),
            Contribuyente(id_contribuyente=3, id_tipo_doc=1, numero_documento="11223344", nombres="Carlos", apellido_paterno="Mamani", apellido_materno="Choque", direccion_fiscal="Calle Secundaria 50", activo=True),
        ]
        for c in contribs:
            existing = db.query(Contribuyente).filter(Contribuyente.id_contribuyente == c.id_contribuyente).first()
            if not existing:
                db.add(c)
        db.commit()

        # ---------- CONTRIBUYENTE_LOTE ----------
        rels = [
            ContribuyenteLote(id_contribuyente=1, id_lote=1, tipo_relacion="PROPIETARIO"),
            ContribuyenteLote(id_contribuyente=2, id_lote=2, tipo_relacion="PROPIETARIO"),
            ContribuyenteLote(id_contribuyente=3, id_lote=3, tipo_relacion="PROPIETARIO"),
        ]
        for rel in rels:
            existing = db.query(ContribuyenteLote).filter(
                ContribuyenteLote.id_contribuyente == rel.id_contribuyente,
                ContribuyenteLote.id_lote == rel.id_lote,
            ).first()
            if not existing:
                db.add(rel)
        db.commit()

        # ---------- USUARIOS ----------
        salt = bcrypt.gensalt()

        admin_user = db.query(Usuario).filter(Usuario.username == "admin1").first()
        if not admin_user:
            admin_hash = bcrypt.hashpw("Admin2026".encode("utf-8"), salt).decode("utf-8")
            admin_user = Usuario(
                id_usuario=1, username="admin1", password_hash=admin_hash,
                nombres="Admin", apellidos="Sistema", id_rol=1,
                email="admin@municipalidad.gob.pe", activo=True, bloqueado=False,
            )
            db.add(admin_user)
            db.commit()

        notif_hash = bcrypt.hashpw("Campo2026".encode("utf-8"), salt).decode("utf-8")
        notif_user = db.query(Usuario).filter(Usuario.username == "notif1").first()
        if not notif_user:
            notif_user = Usuario(
                id_usuario=2, username="notif1", password_hash=notif_hash,
                nombres="Pedro", apellidos="Flores Condori", id_rol=3,
                email="pedro.flores@muni.gob.pe", activo=True, bloqueado=False,
            )
            db.add(notif_user)
            db.commit()
            db.refresh(notif_user)

        # ---------- DEUDAS ----------
        deudas_data = [
            Deuda(id_deuda=101, id_contribuyente=1, id_lote=1, id_tipo_tributo=1, id_estado_cobranza=2, anio_tributo=2026, periodo="202601", monto_original=850.00, saldo_pendiente=850.00, activo=True),
            Deuda(id_deuda=102, id_contribuyente=2, id_lote=2, id_tipo_tributo=1, id_estado_cobranza=3, anio_tributo=2025, periodo="202503", monto_original=2100.00, saldo_pendiente=2100.00, activo=True),
            Deuda(id_deuda=103, id_contribuyente=3, id_lote=3, id_tipo_tributo=2, id_estado_cobranza=2, anio_tributo=2026, periodo="202602", monto_original=450.00, saldo_pendiente=450.00, activo=True),
            Deuda(id_deuda=104, id_contribuyente=1, id_lote=1, id_tipo_tributo=2, id_estado_cobranza=1, anio_tributo=2026, periodo="202603", monto_original=320.00, saldo_pendiente=320.00, activo=True),
            Deuda(id_deuda=105, id_contribuyente=2, id_lote=2, id_tipo_tributo=2, id_estado_cobranza=2, anio_tributo=2026, periodo="202601", monto_original=180.00, saldo_pendiente=180.00, activo=True),
        ]
        for d in deudas_data:
            existing = db.query(Deuda).filter(Deuda.id_deuda == d.id_deuda).first()
            if not existing:
                db.add(d)
        db.commit()

        # ---------- RUTA + DETALLE ----------
        ruta = db.query(RutaNotificacion).filter(RutaNotificacion.id_ruta == 1).first()
        if not ruta:
            from datetime import date
            ruta = RutaNotificacion(
                id_ruta=1, id_usuario=2, fecha_ruta=date.today(),
                estado_ruta="PLANIFICADA", total_deudas=3, distancia_estimada_km=4.5,
            )
            db.add(ruta)
            db.commit()
            db.refresh(ruta)

        detalles = [
            RutaDetalle(id_ruta_detalle=1, id_ruta=1, id_deuda=101, orden_visita=1, visitado=False),
            RutaDetalle(id_ruta_detalle=2, id_ruta=1, id_deuda=102, orden_visita=2, visitado=False),
            RutaDetalle(id_ruta_detalle=3, id_ruta=1, id_deuda=104, orden_visita=3, visitado=False),
        ]
        for det in detalles:
            existing = db.query(RutaDetalle).filter(RutaDetalle.id_ruta_detalle == det.id_ruta_detalle).first()
            if not existing:
                db.add(det)
        db.commit()

        # ---------- PERMISOS ----------
        permisos_data = [
            Permiso(id_permiso=1, codigo="usuarios:gestionar", nombre="Gestion de usuarios", modulo="usuarios"),
            Permiso(id_permiso=2, codigo="rutas:visualizar_propias", nombre="Ver rutas propias", modulo="rutas"),
            Permiso(id_permiso=3, codigo="notificaciones:registrar", nombre="Registrar notificaciones", modulo="notificaciones"),
            Permiso(id_permiso=4, codigo="reportes:descargar", nombre="Descargar reportes", modulo="reportes"),
            Permiso(id_permiso=5, codigo="etl:ejecutar", nombre="Ejecutar ETL", modulo="etl"),
        ]
        for p in permisos_data:
            existing = db.query(Permiso).filter(Permiso.id_permiso == p.id_permiso).first()
            if not existing:
                db.add(p)
        db.commit()

        rol_permisos = [
            RolPermiso(id_rol=1, id_permiso=1), RolPermiso(id_rol=1, id_permiso=2),
            RolPermiso(id_rol=1, id_permiso=3), RolPermiso(id_rol=1, id_permiso=4),
            RolPermiso(id_rol=1, id_permiso=5),
            RolPermiso(id_rol=3, id_permiso=2), RolPermiso(id_rol=3, id_permiso=3),
        ]
        for rp in rol_permisos:
            existing = db.query(RolPermiso).filter(
                RolPermiso.id_rol == rp.id_rol, RolPermiso.id_permiso == rp.id_permiso,
            ).first()
            if not existing:
                db.add(rp)
        db.commit()

        print("=" * 60)
        print("  DATOS DE PRUEBA INSERTADOS CORRECTAMENTE")
        print("=" * 60)
        print()
        print("Credenciales para login:")
        print("  Admin    -> usuario: admin1  | clave: Admin2026")
        print("  Notificador -> usuario: notif1 | clave: Campo2026")
        print()
        print("Para probar NOTIFICACION DE VISITA, inicia sesion como notif1")
        print("y usa estos IDs de deuda en el formulario 'Notificar visita':")
        print()
        print("  ID Deuda | Direccion              | Contribuyente      | Monto S/")
        print("  ---------|------------------------|--------------------|---------")

        deudas = db.query(Deuda).join(Lote, Deuda.id_lote == Lote.id_lote).join(
            Contribuyente, Deuda.id_contribuyente == Contribuyente.id_contribuyente
        ).filter(Deuda.id_deuda.in_([101, 102, 104])).all()

        for d in deudas:
            lote = db.query(Lote).filter(Lote.id_lote == d.id_lote).first()
            contrib = db.query(Contribuyente).filter(Contribuyente.id_contribuyente == d.id_contribuyente).first()
            print(f"  {d.id_deuda:<8} | {lote.direccion:<22} | {contrib.nombres} {contrib.apellido_paterno:<14} | S/ {float(d.saldo_pendiente):.2f}")

        print()
        print("Estados de notificacion disponibles en el combo:")
        print("  1 - NOTIFICADO")
        print("  2 - AUSENTE")
        print("  3 - DIRECCION ERRADA")
        print("  4 - RECHAZADO")
        print("  5 - CONTRIBUYENTE FALLECIDO")
        print()
        print("Configuracion .env necesaria para Redis y API:")
        print("  REDIS_HOST=149.34.48.115")
        print("  REDIS_PORT=6379")
        print("  REDIS_PASSWORD=Upt2026")
        print("  REDIS_CHANNEL=neplatic.rutas")
        print("  WEB_API_BASE_URL=http://localhost:8000")
        print()

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
