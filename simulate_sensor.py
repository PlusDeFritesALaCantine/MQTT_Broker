"""Simulateur de capteurs pour les pays sans capteur physique branché.

Un seul Arduino/DHT22 réel est disponible (Brésil) ; ce script génère des
mesures température/humidité distinctes pour les autres pays, centrées sur
leurs propres conditions idéales (cahier des charges) avec un bruit aléatoire
réaliste (et parfois une dérive plus large pour déclencher des alertes lors
de la démo). Publie sur MQTT exactement comme un vrai capteur le ferait, donc
le pipeline existant (broker -> subscriber.py -> Postgres) reste inchangé.
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
INTERVAL_SECONDES = int(os.getenv("SIMULATEUR_INTERVAL", "60"))

# Conditions idéales par pays (cahier des charges) : centre de la simulation.
PROFILS = {
    "equateur": {"entrepot": "entrepot1", "temperature": 31.0, "humidity": 60.0},
    "colombie": {"entrepot": "entrepot1", "temperature": 26.0, "humidity": 80.0},
}


def generer_mesure(profil: dict) -> dict:
    # La plupart du temps proche de l'idéal, parfois une dérive plus large
    # (~1 fois sur 4) pour produire occasionnellement une vraie alerte.
    amplitude_temp = random.choice([1.5, 1.5, 1.5, 4.5])
    amplitude_hum = random.choice([1.5, 1.5, 1.5, 4.0])
    temperature = round(profil["temperature"] + random.uniform(-amplitude_temp, amplitude_temp), 1)
    humidity = round(profil["humidity"] + random.uniform(-amplitude_hum, amplitude_hum), 1)
    return {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()
    logger.info("Simulateur démarré pour : %s", ", ".join(PROFILS))

    try:
        while True:
            for pays, profil in PROFILS.items():
                topic = f"{pays}/{profil['entrepot']}/mesures"
                payload = json.dumps(generer_mesure(profil))
                client.publish(topic, payload, qos=1)
                logger.info("Publié sur %s : %s", topic, payload)
            time.sleep(INTERVAL_SECONDES)
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
