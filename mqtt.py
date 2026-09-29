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


class MQTT:
    """Classe pour gérer la connexion MQTT et la lecture des données Arduino."""

    def __init__(self):
        """Initialise les paramètres MQTT et Arduino."""
        self.broker = os.getenv("MQTT_BROKER")
        self.port = int(os.getenv("MQTT_PORT"))
        self.port_series = os.getenv("PORT_SERIES")
        self.baud_rate = int(os.getenv("BAUD_RATE"))
        self.mqtt_topic = os.getenv("MQTT_TOPIC")

        self.client = None
        self.arduino = None
        self.running = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback pour la connexion au broker MQTT."""
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            client.subscribe("sensors/#")
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """Callback pour les messages reçus du broker MQTT."""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            logger.info(f"Message reçu sur {topic}: {payload}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message MQTT: {e}")

    def connect_mqtt(self):
        """Se connecte au broker MQTT."""
        try:
            self.client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message

            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            logger.info(f"Connecté au broker MQTT {self.broker}:{self.port}")
        except Exception as e:
            logger.error(f"Impossible de se connecter au Broker : {e}")
            raise

    def connect_arduino(self):
        """Se connecte au port série Arduino."""
        try:
            self.arduino = serial.Serial(self.port_series, self.baud_rate, timeout=1)
            time.sleep(2)
            logger.info(f"Connected to Arduino on {self.port_series}")
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
            raise

    def start(self):
        """Démarre la lecture des données Arduino et la publication MQTT."""
        try:
            self.connect_mqtt()
            self.connect_arduino()
            self.running = True

            logger.info("Script démarré. En attente des données Arduino...")
            while self.running:
                if self.arduino.in_waiting > 0:
                    data = self.arduino.readline().decode("utf-8").strip()
                    if data:
                        try:
                            arduino_json = json.loads(data)
                            if "error" in arduino_json:
                                logger.error(f"Erreur Arduino: {arduino_json['error']}")
                                continue
                            arduino_json["timestamp"] = str(datetime.now())
                            payload = json.dumps(arduino_json)
                            self.client.publish(self.mqtt_topic, payload, qos=1)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON from Arduino: {data}")
                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("Arrêt demandé par l'utilisateur.")
        except Exception as e:
            logger.error(f"Erreur: {e}")
        finally:
            self.stop()

    def stop(self):
        """Arrête la connexion et ferme les ressources."""
        self.running = False

        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            logger.info("Arduino disconnected")

        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT disconnected")


if __name__ == "__main__":
    mqtt_client = MQTT()
    mqtt_client.start()
