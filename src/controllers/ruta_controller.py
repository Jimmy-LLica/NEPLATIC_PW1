from datetime import date, datetime
from src.models.usuario import Usuario
from src.models.deuda import RutaNotificacion, RutaDetalle, Notificacion, Deuda
from src.models.database import get_session
from src.services.event_publisher import EventPublisher
from src.services.redis_publisher import RedisPublisher
from src.services.sync_service import SyncService
from src.utils.logger import setup_logger

logger = setup_logger("ruta")


class RutaController:
    def __init__(self, user: Usuario):
        self.user = user
        self._event_publisher = None
        self._redis_publisher = None
        self._sync_service = None

    @property
    def event_publisher(self):
        if self._event_publisher is None:
            self._event_publisher = EventPublisher()
        return self._event_publisher

    @property
    def redis_publisher(self):
        if self._redis_publisher is None:
            self._redis_publisher = RedisPublisher()
        return self._redis_publisher

    @property
    def sync_service(self):
        if self._sync_service is None:
            self._sync_service = SyncService()
        return self._sync_service

    def listar_rutas_usuario(self):
        with get_session() as db:
            return db.query(RutaNotificacion).filter(
                RutaNotificacion.id_usuario == self.user.id_usuario,
                RutaNotificacion.fecha_ruta >= date.today()
            ).order_by(RutaNotificacion.fecha_ruta.desc()).all()

    def listar_deudas_asignadas(self):
        from src.models.contribuyente import Lote
        with get_session() as db:
            query = db.query(
                RutaDetalle.id_deuda,
                Lote.codigo.label("codigo_lote"),
                RutaDetalle.orden_visita,
                RutaDetalle.visitado
            ).join(
                RutaNotificacion, RutaDetalle.id_ruta == RutaNotificacion.id_ruta
            ).join(
                Deuda, RutaDetalle.id_deuda == Deuda.id_deuda
            ).join(
                Lote, Deuda.id_lote == Lote.id_lote
            ).filter(
                RutaNotificacion.id_usuario == self.user.id_usuario,
                RutaNotificacion.estado_ruta != 'TERMINADA'
            )
            return query.all()

    def registrar_notificacion(self, id_deuda: int, direccion: str, persona: str, parentesco: str, id_estado: int) -> dict:
        with get_session() as db:
            try:
                deuda_existe = db.query(Deuda).filter(Deuda.id_deuda == id_deuda).first()
                if not deuda_existe:
                    return {"success": False, "message": f"La deuda con ID {id_deuda} no existe en el sistema."}

                notif = Notificacion(
                    id_deuda=id_deuda,
                    id_usuario=self.user.id_usuario,
                    id_estado_notif=id_estado,
                    hora_notificacion=datetime.now().strftime("%H:%M:%S"),
                    direccion_visitada=direccion.strip(),
                    persona_contactada=persona.strip(),
                    parentesco=parentesco.strip(),
                )
                db.add(notif)
                db.commit()
                db.refresh(notif)
                logger.info("Notificacion registrada: deuda %s, estado %s, id=%s", id_deuda, id_estado, notif.id_notificacion)

                payload = {
                    "id_notificacion": notif.id_notificacion,
                    "id_deuda": id_deuda,
                    "id_usuario": self.user.id_usuario,
                    "id_estado_notif": id_estado,
                    "direccion_visitada": direccion.strip(),
                    "persona_contactada": persona.strip(),
                    "parentesco": parentesco.strip(),
                    "fecha_registro": notif.fecha_registro.isoformat() if notif.fecha_registro else datetime.now().isoformat(),
                }

                outbox_id = self.event_publisher.publish(
                    aggregate_type="notificacion",
                    aggregate_id=str(notif.id_notificacion),
                    event_type="VisitaRegistrada",
                    payload=payload,
                )

                redis_ok = self.redis_publisher.publish(
                    event_type="VisitaRegistrada",
                    aggregate_id=str(notif.id_notificacion),
                    payload=payload,
                )

                sync_result = self.sync_service.sincronizar_notificacion(payload)

                detalle = db.query(RutaDetalle).filter(
                    RutaDetalle.id_deuda == id_deuda,
                    RutaDetalle.visitado == False,
                ).first()
                if detalle:
                    detalle.visitado = True
                    detalle.id_notificacion = notif.id_notificacion
                    db.commit()

                logger.info(
                    "Flujo completo: outbox=%s, redis=%s, sync_api=%s",
                    "ok" if outbox_id else "fallo",
                    "ok" if redis_ok else "fallo",
                    sync_result.get("status", "?"),
                )

                return {
                    "success": True,
                    "message": "Visita registrada correctamente.",
                    "id_notificacion": notif.id_notificacion,
                    "outbox_id": outbox_id,
                    "redis_published": redis_ok,
                    "sync_status": sync_result.get("status"),
                    "sync_message": sync_result.get("message"),
                }

            except Exception as e:
                db.rollback()
                logger.error("Error al registrar notificacion: %s", e)
                return {"success": False, "message": f"Error: {e}"}

    def close(self):
        try:
            self.redis_publisher.close()
        except Exception:
            pass
