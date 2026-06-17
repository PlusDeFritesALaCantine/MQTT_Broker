"""Subscriber MQTT : écoute les mesures capteur sur EMQX et les persiste en base.

Topic attendu : bresil/<entrepot>/mesures (ex: bresil/entrepot1/mesures)
Payload attendu : {"temperature": 29.5, "humidity": 54.2, "timestamp": "..."}

Écrit directement dans la table `mesures` (schéma utilisé par api_futurekawa),
en SQL brut pour ne pas dépendre des modèles ORM de ce repo qui suivent un
schéma différent (countries/warehouses/sensors).
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_URL = os.getenv("DB_URL")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_MESURES = os.getenv("MQTT_TOPIC_MESURES", "bresil/+/mesures")

if not DB_URL:
    raise ValueError("DB_URL is not set in environment variables")

engine = create_engine(DB_URL, pool_pre_ping=True)

INSERT_MESURE = text(
    "INSERT INTO mesures (id, entrepot_id, temperature, humidity, timestamp) "
    "VALUES (:id, :entrepot_id, :temperature, :humidity, :timestamp)"
)


def entrepot_id_from_topic(topic: str) -> str:
    """bresil/entrepot1/mesures -> entrepot-bresil-1"""
    segment = topic.split("/")[1] if "/" in topic else topic
    match = re.search(r"(\d+)$", segment)
    suffix = match.group(1) if match else "1"
    return f"entrepot-bresil-{suffix}"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connecté au broker MQTT %s:%s", MQTT_BROKER, MQTT_PORT)
        client.subscribe(MQTT_TOPIC_MESURES, qos=1)
        logger.info("Abonné au topic %s", MQTT_TOPIC_MESURES)
    else:
        logger.error("Échec de connexion au broker, code %s", rc)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("Payload JSON invalide sur %s: %r", msg.topic, msg.payload)
        return

    temperature = payload.get("temperature")
    humidity = payload.get("humidity")
    if temperature is None or humidity is None:
        logger.error("Payload incomplet sur %s: %r", msg.topic, payload)
        return

    timestamp = payload.get("timestamp") or datetime.now(timezone.utc).isoformat()
    entrepot_id = entrepot_id_from_topic(msg.topic)

    try:
        with engine.begin() as conn:
            conn.execute(
                INSERT_MESURE,
                {
                    "id": f"M-{uuid.uuid4().hex[:12]}",
                    "entrepot_id": entrepot_id,
                    "temperature": float(temperature),
                    "humidity": float(humidity),
                    "timestamp": timestamp,
                },
            )
        logger.info(
            "Mesure insérée [%s] temp=%.1f hum=%.1f", entrepot_id, temperature, humidity
        )
    except Exception:
        logger.exception("Échec de l'insertion en base pour %s", msg.topic)


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    logger.info("Démarrage du subscriber, en attente de messages...")
    client.loop_forever()


if __name__ == "__main__":
    main()
