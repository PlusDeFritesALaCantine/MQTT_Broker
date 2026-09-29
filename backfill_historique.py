"""Backfill d'un historique de mesures simulées pour Équateur et Colombie.

Génère plusieurs heures de relevés passés (un point toutes les quelques
minutes), en variant autour de la température/humidité moyenne (idéale,
cahier des charges) de chaque pays, pour enrichir les courbes du front sans
attendre que le simulateur temps réel (simulate_sensor.py) accumule les
points minute par minute.
"""

import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL is not set in environment variables")

engine = create_engine(DB_URL, pool_pre_ping=True)

INSERT_MESURE = text(
    "INSERT INTO mesures (id, entrepot_id, temperature, humidity, timestamp) "
    "VALUES (:id, :entrepot_id, :temperature, :humidity, :timestamp)"
)

# Température / humidité moyenne (idéale) par pays, cahier des charges.
PROFILS = {
    "equateur": {"entrepot_id": "entrepot-equateur-1", "temperature": 31.0, "humidity": 60.0},
    "colombie": {"entrepot_id": "entrepot-colombie-1", "temperature": 26.0, "humidity": 80.0},
}

DUREE_HEURES = 6
PAS_MINUTES = 5


def generer_valeur(moyenne_temp: float, moyenne_hum: float) -> tuple[float, float]:
    # La plupart du temps proche de la moyenne, parfois une dérive plus large
    # (~1 fois sur 4) pour produire occasionnellement une vraie alerte.
    amplitude_temp = random.choice([1.5, 1.5, 1.5, 4.5])
    amplitude_hum = random.choice([1.5, 1.5, 1.5, 4.0])
    temperature = round(moyenne_temp + random.uniform(-amplitude_temp, amplitude_temp), 1)
    humidity = round(moyenne_hum + random.uniform(-amplitude_hum, amplitude_hum), 1)
    return temperature, humidity


def main():
    now = datetime.now(timezone.utc)
    debut = now - timedelta(hours=DUREE_HEURES)
    inserted = 0

    with engine.begin() as conn:
        for pays, profil in PROFILS.items():
            t = debut
            while t <= now:
                temperature, humidity = generer_valeur(profil["temperature"], profil["humidity"])
                conn.execute(
                    INSERT_MESURE,
                    {
                        "id": f"M-{uuid.uuid4().hex[:12]}",
                        "entrepot_id": profil["entrepot_id"],
                        "temperature": temperature,
                        "humidity": humidity,
                        "timestamp": t,
                    },
                )
                inserted += 1
                t += timedelta(minutes=PAS_MINUTES)
            print(f"{pays}: historique généré ({profil['temperature']}°C / {profil['humidity']}% en moyenne)")

    print(f"Total : {inserted} mesures historiques insérées.")


if __name__ == "__main__":
    main()
