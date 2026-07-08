"""Session capteur en direct : crée un nouveau Lot Brésil dans la base du dashboard
(SQLite, api_futurekawa/futurekawa.db) et y enregistre chaque relevé DHT22 réel au
fil de l'eau, visible immédiatement sur le site (dashboard, page Lots, fiche du lot).

Lancement : un nouveau Lot est créé avec la date du jour et un entrepôt dédié à
cette session (pour ne pas mélanger ses mesures avec celles des autres lots/sessions).

Arrêt (Ctrl+C) : calcule la moyenne température/humidité de la session, l'affiche,
et la reporte dans le champ "exploitation" du lot pour qu'elle reste visible sur le
site sans changement de schéma. Le lot et ses mesures restent en base.

Usage : python session_lot.py
"""

import json
import os
import signal
import sqlite3
import time
import uuid
from datetime import date, datetime


def _demander_arret(signum, frame):
    raise KeyboardInterrupt


# SIGINT (Ctrl+C) et SIGTERM (ex: `kill <pid>`, ou un job lancé en arrière-plan qui
# n'a plus de terminal attaché) doivent tous les deux déclencher un arrêt propre
# (moyenne + mise à jour du lot), pas une coupure brute.
signal.signal(signal.SIGINT, _demander_arret)
signal.signal(signal.SIGTERM, _demander_arret)

import serial
from dotenv import load_dotenv

load_dotenv()

PORT_SERIES = os.getenv("PORT_SERIES", "/dev/ttyACM0")
BAUD_RATE = int(os.getenv("BAUD_RATE", "9600"))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "api_futurekawa", "futurekawa.db")

SESSION_ID = datetime.now().strftime("%Y%m%d-%H%M%S")
LOT_ID = f"LOT-BR-LIVE-{SESSION_ID}"
ENTREPOT_ID = f"entrepot-bresil-live-{SESSION_ID}"
EXPLOITATION_DE_BASE = "Fazenda Sol - Session capteur live"


def creer_lot(con: sqlite3.Connection) -> None:
    con.execute(
        "INSERT INTO lots (id, pays, exploitation, entrepot_id, date_stockage, statut) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (LOT_ID, "bresil", EXPLOITATION_DE_BASE, ENTREPOT_ID, date.today().isoformat(), "conforme"),
    )
    con.commit()


def enregistrer_mesure(con: sqlite3.Connection, temperature: float, humidity: float) -> datetime:
    timestamp = datetime.now()
    con.execute(
        "INSERT INTO mesures (id, entrepot_id, temperature, humidity, timestamp) VALUES (?, ?, ?, ?, ?)",
        (f"M-{uuid.uuid4().hex[:12]}", ENTREPOT_ID, temperature, humidity, str(timestamp)),
    )
    con.commit()
    return timestamp


def cloturer_lot(con: sqlite3.Connection, moyenne_temp: float, moyenne_hum: float) -> None:
    resume = f"{EXPLOITATION_DE_BASE} (moyenne {moyenne_temp:.1f}°C / {moyenne_hum:.1f}%)"
    con.execute("UPDATE lots SET exploitation = ? WHERE id = ?", (resume, LOT_ID))
    con.commit()


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    creer_lot(con)
    print(f"Lot créé : {LOT_ID} (entrepôt {ENTREPOT_ID}, date {date.today().isoformat()})")
    print(f"A suivre en direct sur : http://127.0.0.1:5173/lots/bresil/{LOT_ID}")

    arduino = serial.Serial(PORT_SERIES, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Connecté à l'Arduino. Lecture en cours... (Ctrl+C pour arrêter et calculer la moyenne)\n")

    temperatures: list[float] = []
    humidities: list[float] = []

    try:
        while True:
            if arduino.in_waiting > 0:
                raw = arduino.readline().decode("utf-8", errors="replace").strip()
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if "error" in payload:
                    print(f"Capteur : {payload['error']}")
                    continue
                temperature = float(payload["temperature"])
                humidity = float(payload["humidity"])
                timestamp = enregistrer_mesure(con, temperature, humidity)
                temperatures.append(temperature)
                humidities.append(humidity)
                print(
                    f"[{len(temperatures):>3}] {timestamp:%H:%M:%S} "
                    f"temp={temperature:.1f}°C hum={humidity:.1f}%"
                )
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nArrêt demandé, calcul de la moyenne...")
    finally:
        arduino.close()
        if temperatures:
            moyenne_temp = sum(temperatures) / len(temperatures)
            moyenne_hum = sum(humidities) / len(humidities)
            cloturer_lot(con, moyenne_temp, moyenne_hum)
            print("\n=== Résumé de la session ===")
            print(f"Lot            : {LOT_ID}")
            print(f"Mesures        : {len(temperatures)}")
            print(f"Temp. moyenne  : {moyenne_temp:.1f}°C")
            print(f"Humidité moy.  : {moyenne_hum:.1f}%")
            print(f"Dashboard      : http://127.0.0.1:5173/lots/bresil/{LOT_ID}")
        else:
            print("\nAucune mesure capturée durant cette session (le lot reste en base, vide).")
        con.close()


if __name__ == "__main__":
    main()
