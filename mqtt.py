import json
import logging
import os
import time
from datetime import datetime

import paho.mqtt.client as mqtt
import serial
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
PORT_SERIES = os.getenv('PORT_SERIES')
BAUD_RATE = int(os.getenv('BAUD_RATE'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC')

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
        client.subscribe("sensors/#")
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        logger.info(f"Message reçu sur {topic}: {payload}")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message MQTT: {e}")

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    logger.error(f"Impossible de se connecter au Broker : {e}")
    exit(1)

try:
    arduino = serial.Serial(PORT_SERIES, BAUD_RATE, timeout=1)
    time.sleep(2)
    logger.info(f"Connected to Arduino on {PORT_SERIES}")
except Exception as e:
    logger.error(f"Failed to connect to Arduino: {e}")
    client.loop_stop()
    client.disconnect()
    exit(1)

logger.info("Script démarré. En attente des données Arduino...")
try:
    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().decode('utf-8').strip()
            if data:
                try:
                    arduino_json = json.loads(data)
                    if "error" in arduino_json:
                        logger.error(f"Erreur Arduino: {arduino_json['error']}")
                        continue
                    arduino_json["timestamp"] = str(datetime.now())
                    payload = json.dumps(arduino_json)
                    client.publish(MQTT_TOPIC, payload, qos=1)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from Arduino: {data}")
        time.sleep(0.01)

except KeyboardInterrupt:
    logger.info("Arrêt demandé par l'utilisateur.")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
    client.loop_stop()
    client.disconnect()
