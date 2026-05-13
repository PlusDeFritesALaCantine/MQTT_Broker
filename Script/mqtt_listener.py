import paho.mqtt.client as mqtt
from datetime import datetime
from models import Session, Mesure, engine, Base
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(engine)

current_mesures = {}

class MQTTListener:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            client.subscribe("sensors/#")
        else:
            logger.error(f"Failed to connect, return code {rc}")
    
    def on_message(client, userdata, msg):
        global current_mesures
        topic = msg.topic