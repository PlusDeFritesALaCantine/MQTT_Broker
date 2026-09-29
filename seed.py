"""Script pour initialiser la base de données avec des données de test."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from database import SessionLocal, init_db
from models.country import Country
from models.exploitation import Exploitation
from models.lot import Lot
from models.warehouse import Warehouse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database():
    """Ajoute des données initiales à la base de données."""
    db = SessionLocal()
    try:
        init_db()
        logger.info("Tables créées avec succès")

        if db.query(Country).first():
            logger.info("Les données existent déjà, abandon du seeding")
            return

        brasil = Country(
            code="BR",
            name="Brasil",
            ideal_temperature=20,
            ideal_humidity=60,
            temperature_tolerance=5,
            humidity_tolerance=15,
        )
        equateur = Country(
            code="EQ",
            name="Equateur",
            ideal_temperature=22,
            ideal_humidity=55,
            temperature_tolerance=5,
            humidity_tolerance=15,
        )
        columbia = Country(
            code="CO",
            name="Columbia",
            ideal_temperature=21,
            ideal_humidity=58,
            temperature_tolerance=5,
            humidity_tolerance=15,
        )

        db.add_all([brasil, equateur, columbia])
        db.commit()
        logger.info("Pays créés")

        exp_loire = Exploitation(
            country_id=brasil.id,
            name="Loire Valley Exploitation",
            location="Loire Valley, France",
        )
        exp_douro = Exploitation(
            country_id=equateur.id,
            name="Douro Valley Exploitation",
            location="Douro Valley, Spain",
        )
        exp_columbia = Exploitation(
            country_id=columbia.id,
            name="Columbia Valley Exploitation",
            location="Columbia Valley, Colombia",
        )
        db.add_all([exp_loire, exp_douro, exp_columbia])
        db.commit()
        logger.info("Exploitations créées")

        warehouse_loire = Warehouse(
            exploitation_id=exp_loire.id,
            name="Loire Central Warehouse",
            address="123 Rue de la Vigne, 49000 Angers",
            manager_mail="manager.loire@example.com",
        )
        warehouse_douro = Warehouse(
            exploitation_id=exp_douro.id,
            name="Douro Storage",
            address="456 Camino del Vino, 28000 Madrid",
            manager_mail="manager.douro@example.com",
        )
        warehouse_columbia = Warehouse(
            exploitation_id=exp_columbia.id,
            name="Columbia Storage",
            address="789 Carrera del Café, 11000 Bogotá",
            manager_mail="manager.columbia@example.com",
        )
        db.add_all([warehouse_loire, warehouse_douro, warehouse_columbia])
        db.commit()
        logger.info("Entrepôts créés")

        now = datetime.now()
        lot_1 = Lot(
            lot_code="LOT-2024-001",
            warehouse_id=warehouse_loire.id,
            stored_at=now,
        )
        lot_2 = Lot(
            lot_code="LOT-2024-002",
            warehouse_id=warehouse_douro.id,
            stored_at=now - timedelta(days=5),
        )
        lot_3 = Lot(
            lot_code="LOT-2024-003",
            warehouse_id=warehouse_columbia.id,
            stored_at=now - timedelta(days=10),
        )
        db.add_all([lot_1, lot_2, lot_3])
        db.commit()
        logger.info("Lots créés")

        logger.info("Alertes créées")

        logger.info("Seeding terminé avec succès !")

    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors du seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
