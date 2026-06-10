import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.etl.oracle_extractor import OracleExtractor
from src.services.etl.postgres_loader import PostgresLoader
from src.utils.logger import setup_logger

logger = setup_logger("etl-main")


def run_etl():
    oracle_dsn = os.getenv("ORACLE_DSN")
    oracle_user = os.getenv("ORACLE_USER")
    oracle_pwd = os.getenv("ORACLE_PWD")

    if not all([oracle_dsn, oracle_user, oracle_pwd]):
        logger.error("Variables ORACLE_DSN, ORACLE_USER y ORACLE_PWD requeridas")
        return False

    extractor = OracleExtractor(oracle_dsn, oracle_user, oracle_pwd)
    loader = PostgresLoader()

    try:
        extractor.connect()
        logger.info("Extrayendo deudas desde Oracle...")
        deudas = extractor.extract_deudas()
        logger.info(f"{len(deudas)} deudas extraídas")
        loader.load_deudas(deudas, lote_etl="ETL_DIARIO")
        logger.info("ETL completado exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error en ETL: {e}")
        return False
    finally:
        extractor.close()
        loader.close()


if __name__ == "__main__":
    run_etl()