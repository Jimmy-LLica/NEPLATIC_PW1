from sqlalchemy import text
from src.models.database import get_session
from src.utils.logger import setup_logger

logger = setup_logger("reportes")


class ReporteController:
    def __init__(self):
        pass

    def dashboard_gerencial(self) -> dict:
        with get_session() as db:
            result = db.execute(text("SELECT * FROM neplatic.v_dashboard_gerencial")).first()
            if result:
                return dict(result._mapping)
            return {}

    def morosidad_por_sector(self):
        with get_session() as db:
            return db.execute(text("SELECT * FROM neplatic.v_morosidad_sector")).fetchall()

    def morosidad_por_manzana(self, id_sector: int = None):
        with get_session() as db:
            if id_sector:
                query = text("""
                    SELECT *
                    FROM neplatic.v_morosidad_manzana
                    WHERE codigo_sector = (
                        SELECT codigo
                        FROM neplatic.sector
                        WHERE id_sector = :id_sector
                    )
                """)
                return db.execute(query, {"id_sector": id_sector}).fetchall()
            return db.execute(text("SELECT * FROM neplatic.v_morosidad_manzana")).fetchall()

    def top_deudores(self, limit: int = 10):
        with get_session() as db:
            return db.execute(text("SELECT * FROM neplatic.v_top_deudores LIMIT :limit"), {"limit": limit}).fetchall()

    def evolucion_mensual(self):
        with get_session() as db:
            return db.execute(text("SELECT * FROM neplatic.v_evolucion_morosidad")).fetchall()

    def close(self):
        pass

    def exportable_dashboard(self) -> dict:
        return {
            "dashboard": self.dashboard_gerencial(),
            "top_deudores": [dict(row._mapping) for row in self.top_deudores(10)],
            "sector": [dict(row._mapping) for row in self.morosidad_por_sector()],
            "evolucion": [dict(row._mapping) for row in self.evolucion_mensual()],
        }
