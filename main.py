import logging

from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Initialisation de la base de données...")
    init_db()

    # logger.info("Démarrage du broker MQTT...")
    # mqtt = MQTT()
    # return mqtt

if __name__ == "__main__":
    main()
