import logging
from models.lot import Lot
from models.alerte import Alerte
from models.warehouse import Warehouse
from models.exploitation import Exploitation
from models.iot_sensor import IotSensor
from models.country import Country
from models.sensor_reading import SensorReading


from database import init_db
from mqtt import MQTT

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