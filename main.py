import logging
import sys

from database import init_db
from mqtt import MQTT
from seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Initialisation de la base de données...")
    init_db()

    # Optionnel : ajouter des données de test
    if len(sys.argv) > 1 and sys.argv[1] == "--seed":
        logger.info("Ajout des données initiales...")
        seed_database()

    logger.info("Démarrage du broker MQTT...")
    mqtt = MQTT()
    return mqtt


if __name__ == "__main__":
    main()
