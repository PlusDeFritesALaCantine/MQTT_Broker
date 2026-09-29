# Brocker MQTT

A complete IoT data management system combining an MQTT broker (EMQX), PostgreSQL database, and Python application for collecting, processing, and storing sensor data.
A complete IoT data management system combining an MQTT broker (EMQX), PostgreSQL database, and Python application for collecting, processing, and storing sensor data.

## Objective

This project provides a foundation to:
- Run and test an MQTT broker locally (EMQX)
- Manage IoT sensors and sensor readings
- Store IoT data in PostgreSQL
- Process alerts and warehouse management
- Simplify MQTT client development and integration

## Project Features

- **MQTT Broker**: EMQX containerized broker for message brokering, one topic per country
  (`<pays>/<entrepot>/mesures`, e.g. `bresil/entrepot1/mesures`)
- **Database**: PostgreSQL (via Podman Compose) for persistent storage of sensor readings and lots,
  plus PgAdmin (web UI) and Mailpit (fake SMTP server for alert emails, see `api_futurekawa`)
- **Serial → MQTT bridge** (`mqtt.py`): reads the real DHT22 sensor (Brazil) over serial and
  publishes each reading to MQTT, exactly as `sketch_may6a` (see `arduino/`) outputs it
- **Simulated sensors** (`simulate_sensor.py`): generates realistic readings for the countries
  without a physical sensor (Équateur, Colombie), published on MQTT the same way a real
  sensor would, so the rest of the pipeline is unaware of the difference
- **Historical backfill** (`backfill_historique.py`): generates several hours of past
  readings for Équateur/Colombie so the front-end charts aren't empty while waiting for
  the simulator to accumulate data minute by minute
- **MQTT → Postgres subscriber** (`subscriber.py`): listens to all three countries'
  topics (wildcard `+/+/mesures`) and persists every reading into the `mesures` table of
  the schema used by `api_futurekawa` (not the ORM models below — see note in
  [Data Models](#data-models))
- **Live sensor sessions** (`session_lot.py`): self-contained capture session for the real
  DHT22 sensor — creates a dated `Lot` for Brazil on launch, streams each reading to the
  terminal and directly into the front-end's SQLite dashboard database while it runs, and
  computes + reports a temperature/humidity average onto the lot when the session is
  stopped (`Ctrl+C`); see [Live sensor session](#live-sensor-session-session_lotpy)
- **Seed data** (`seed.py`): populate demo Country/Exploitation/Warehouse/Lot data for
  the 3 countries (`models/` schema — see the `api_futurekawa` repo for `seed.sql` /
  `seed_sqlite.py`, which seed the flatter `lots`/`mesures` schema instead)
- **Environment Configuration**: Flexible configuration via `.env` file

## Prerequisites

- Windows, Linux, or macOS
- Podman + `podman-compose` (or Docker + Docker Compose — `docker-compose.yml` is
  compatible with either) for running EMQX, PostgreSQL, PgAdmin and Mailpit
- Python 3.9 or higher
- A terminal (PowerShell, CMD, Bash)
- An MQTT client for testing (EMQX MQTTX Web view or `mqttx` CLI)
- For the real sensor scripts (`mqtt.py`, `session_lot.py`): an Arduino Uno running
  `arduino/sketch_may6a` and connected over USB (`/dev/ttyACM0` on Linux, `COMx` on Windows)

## Quick Start

### 1. Clone the repository
### 1. Clone the repository

```bash
git clone <repository-url>
cd brocker-mqtt
```
```bash
git clone <repository-url>
cd brocker-mqtt
```

### 2. Install Python dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv .venv

# On Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# On macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e .
```

Or manually:

```bash
pip install paho-mqtt>=2.1.0 psycopg[binary]>=3.2.13 pyserial>=3.5 python-dotenv>=1.2.1 sqlalchemy>=2.0.49
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
# Topic published by mqtt.py for THIS bridge (one physical sensor = one country/entrepôt).
MQTT_TOPIC=bresil/entrepot1/mesures
# Topic pattern listened to by subscriber.py (wildcard on country+entrepôt to cover all 3).
MQTT_TOPIC_MESURES=+/+/mesures

# Serial Port Configuration
PORT_SERIES=/dev/ttyACM0  # On Windows: COM3, etc.
BAUD_RATE=9600

# Database Configuration (5433 = host port mapped to Postgres' 5432 in docker-compose.yml)
DB_URL=postgresql+psycopg://postgres:postgres@localhost:5433/iot_data
```

### 4. Start the services

```bash
podman-compose up -d
# or: docker-compose up -d
```

This will start:
- **EMQX Broker** on port `1883` (MQTT) and `18083` (Web Console)
- **PostgreSQL** on port `5433` (mapped from the container's `5432`)
- **PgAdmin** on port `8080` (a `iot_data (FutureKawa)` server is pre-registered)
- **Mailpit** on port `8025` (fake SMTP server that captures the alert emails sent by
  `api_futurekawa`, UI) and `1025` (SMTP)

### 5. Initialize the database

```bash
python main.py
```
```bash
python main.py
```

### 6. Verify the setup

- **EMQX Web Console**: Open http://localhost:18083 (default: admin/public)
- **MQTT Testing**: Subscribe to a topic:
### 6. Verify the setup

- **EMQX Web Console**: Open http://localhost:18083 (default: admin/public)
- **MQTT Testing**: Subscribe to a topic:

```bash
mqttx sub -h localhost -p 1883 -t sensors/+
```

In another terminal, publish a test message:

```bash
mqttx pub -h localhost -p 1883 -t sensors/test -m '{"sensor_id": 1, "value": 25.5}'
```

## Project Structure

```
brocker-mqtt/
├── main.py                  # Entry point: init DB (ORM models below) + optional seed + MQTT client
├── mqtt.py                  # Serial (real DHT22) -> MQTT bridge, one topic per country
├── subscriber.py            # MQTT (all 3 countries) -> Postgres `mesures` (api_futurekawa schema)
├── simulate_sensor.py       # Simulated MQTT publisher for Équateur/Colombie
├── backfill_historique.py   # One-shot historical backfill for Équateur/Colombie
├── session_lot.py           # Live capture session: creates a dated Lot + streams real
│                             # readings straight into the front-end's SQLite database
├── seed.py                  # Seeds Country/Exploitation/Warehouse/Lot demo data (ORM models)
├── database.py              # Database setup and session management
├── docker-compose.yml       # Services: EMQX, PostgreSQL, PgAdmin, Mailpit
├── pyproject.toml          # Python project metadata and dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
└── models/                 # SQLAlchemy ORM models (Country/Exploitation/Warehouse/...)
    ├── __init__.py
    ├── alerte.py           # Alert model
    ├── country.py          # Country model
    ├── exploitation.py     # Exploitation/Farm model
    ├── iot_sensor.py       # IoT sensor model
    ├── lot.py              # Lot/Batch model
    ├── sensor_reading.py   # Sensor reading/measurement model
    └── warehouse.py        # Warehouse model
```

## Configuration

### Environment Variables

Key configuration items in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `MQTT_BROKER` | MQTT broker address | `localhost` |
| `MQTT_PORT` | MQTT broker port | `1883` |
| `MQTT_TOPIC` | Topic published by mqtt.py for this bridge | `bresil/entrepot1/mesures` |
| `MQTT_TOPIC_MESURES` | Topic pattern subscriber.py listens to | `+/+/mesures` |
| `PORT_SERIES` | Serial port for sensor data input | `/dev/ttyACM0` or `COM3` |
| `BAUD_RATE` | Serial port baud rate | `9600` |
| `DB_URL` | PostgreSQL connection URL | `postgresql+psycopg://user:pass@host:5433/iot_data` |

### Container Services

**EMQX Configuration:**
- Default admin credentials: `admin` / `Kawa-Emqx-2026`
- MQTT port: `1883`
- WebSocket port: `8083`
- Secure port: `8084`
- Web console: `http://localhost:18083`

**PostgreSQL Configuration:**
- Default user: `postgres`
- Default password: `postgres`
- Default database: `iot_data`
- Host port: `5433` (container's internal port stays `5432`)

**PgAdmin:** `http://localhost:8080` (`pgadmin4@pgadmin.org` / `admin`), server `iot_data
(FutureKawa)` pre-registered.

**Mailpit:** `http://localhost:8025` (fake SMTP UI, no auth) — captures the alert emails
sent by `api_futurekawa`.

## Data Models

`models/` defines a richer relational schema (entities below), created by `main.py`/`seed.py`:

- **IotSensor**: Represents connected IoT sensors with metadata
- **SensorReading**: Records measurements from sensors (temperature, humidity, etc.)
- **Alerte**: Stores alerts triggered by sensor values
- **Exploitation**: Represents farms or production facilities
- **Warehouse**: Storage facility information
- **Lot**: Batch or production lot tracking
- **Country**: Geographic location data

⚠️ The live pipeline (`subscriber.py`, `session_lot.py`) does **not** write through these
ORM models. It writes directly (raw SQL / `sqlite3`) into the flatter `lots` / `mesures`
schema defined and consumed by `api_futurekawa` (`id, pays, exploitation, entrepot_id,
date_stockage, statut` / `id, entrepot_id, temperature, humidity, timestamp`), so that
readings are immediately visible through the API and front-end without depending on this
repo's ORM layer.

## Core Components

### main.py
Entry point that initializes the `models/` schema and, with `--seed`, calls `seed.py`, then starts the MQTT client.

### mqtt.py
Reads the real DHT22 sensor over serial (`PORT_SERIES`) and republishes each reading as
JSON on the country's MQTT topic (`MQTT_TOPIC`, e.g. `bresil/entrepot1/mesures`).

### subscriber.py
Subscribes to every country's topic (`+/+/mesures`) and inserts each reading into the
`mesures` table (api_futurekawa schema), deriving the `entrepot_id` from the topic
(`bresil/entrepot1/mesures` → `entrepot-bresil-1`).

### simulate_sensor.py
Publishes simulated readings for the countries without a physical sensor (Équateur,
Colombie), centered on each country's ideal temperature/humidity with realistic noise
and occasional drift (to trigger demo alerts).

### backfill_historique.py
One-shot script that inserts several hours of simulated past readings for Équateur/Colombie directly into Postgres.

### session_lot.py
Self-contained live capture session for the real sensor — see
[Live sensor session](#live-sensor-session-session_lotpy) below.

### database.py
Manages PostgreSQL connection using SQLAlchemy ORM (used by `models/`, `main.py`, `seed.py`).

## Live sensor session (`session_lot.py`)

Turns a run of the physical DHT22 sensor into a new, dated coffee lot that shows up on
the dashboard, instead of only appending to an existing entrepôt's history:

- **On launch**: creates a new `Lot` for Brazil (`pays=bresil`) dated today, with a
  session-specific `entrepot_id` (so its readings never mix with another lot/session),
  directly in the SQLite database the front-end/API read from
  (`api_futurekawa/futurekawa.db`).
- **While running**: each real reading is printed to the terminal
  (`[n] HH:MM:SS temp=... hum=...`) and inserted into that lot's measures immediately —
  the lot's chart on the front-end (`/lots/bresil/<lot_id>`) updates live on refresh.
- **On stop** (`Ctrl+C`, or `SIGTERM`): computes the session's average temperature and
  humidity, prints a summary, and reports the average into the lot's `exploitation`
  field so it stays visible on the site without any schema change.

```bash
cd MQTT_Broker
. .venv/bin/activate
python session_lot.py
```

Requires the API/front-end (`api_futurekawa`, `backend_futurekawa`, `front_futurekawa`)
to be pointed at the same SQLite file to see the lot appear (see `start_all.sh` / each
repo's README). Only one process can hold the serial port at a time — stop `mqtt.py` (or
`arduino-cli monitor`) before running `session_lot.py`, and vice versa.

## Development Best Practices

- Always use environment variables for sensitive data (DB credentials, MQTT settings)
- Version `.env.example` but never commit `.env` with real credentials
- Test MQTT message flow before deploying to production
- Implement proper error handling and logging for sensor failures
- Document schema changes to ORM models
- Use PostgreSQL connection pooling for production environments
- Validate sensor data before storing in the database
- Monitor MQTT broker logs for connection issues

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| **Port already in use** | Another service using the same port | Change the port in `docker-compose.yml` or stop the conflicting process |
| **MQTT connection refused** | Broker not running or wrong host/port | Verify `docker-compose up -d` completed and check `.env` settings |
| **Database connection error** | PostgreSQL not running or wrong credentials | Check `docker ps` and verify `DB_URL` in `.env` |
| **No message received** | Topic mismatch or wrong subscriptions | Check topic names in code and MQTT client |
| **Serial port not found** | Device not connected or wrong port name | List available ports with `python -m serial.tools.list_ports` |
| **Encoding issues** | Character encoding mismatch in data | Ensure UTF-8 encoding in `.env` and database |

### Debugging

Check logs from services:

```bash
# EMQX logs
docker logs emqx-broker

# PostgreSQL logs
docker logs postgres-db

# Application logs
python main.py
```

List active containers:

```bash
docker-compose ps
```

Connect to PostgreSQL for direct inspection:

```bash
psql -h localhost -p 5433 -U postgres -d iot_data
# or, without a local psql install:
podman exec -it postgres-db psql -U postgres -d iot_data
```

## Dependencies

### Core Libraries

- **paho-mqtt** (>=2.1.0): Python MQTT client library
- **psycopg** (>=3.2.13): PostgreSQL adapter for Python
- **sqlalchemy** (>=2.0.49): Python SQL toolkit and Object Relational Mapper
- **pyserial** (>=3.5): Serial port communication
- **python-dotenv** (>=1.2.1): Load environment variables from `.env` file

See `pyproject.toml` for full dependency list.

## Contributing
## Contributing

1. Create a working branch: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Update documentation if needed
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to the branch and open a pull request with a clear description
1. Create a working branch: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Update documentation if needed
4. Commit with clear messages: `git commit -m "Add feature description"`
5. Push to the branch and open a pull request with a clear description

## License

[Specify your project license here - e.g., MIT, Apache-2.0, GPL-3.0, or proprietary]

## Support

For issues, questions, or suggestions:
- Check the [Troubleshooting](#troubleshooting) section
- Review EMQX documentation: https://docs.emqx.com/
- Check SQLAlchemy documentation: https://docs.sqlalchemy.org/
[Specify your project license here - e.g., MIT, Apache-2.0, GPL-3.0, or proprietary]

## Support

For issues, questions, or suggestions:
- Check the [Troubleshooting](#troubleshooting) section
- Review EMQX documentation: https://docs.emqx.com/
- Check SQLAlchemy documentation: https://docs.sqlalchemy.org/
