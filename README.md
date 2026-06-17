# Brocker MQTT

A complete IoT data management system combining an MQTT broker (EMQX), PostgreSQL database, and Python application for collecting, processing, and storing sensor data.

## Objective

This project provides a foundation to:
- Run and test an MQTT broker locally (EMQX)
- Manage IoT sensors and sensor readings
- Store IoT data in PostgreSQL
- Process alerts and warehouse management
- Simplify MQTT client development and integration

## Project Features

- **MQTT Broker**: EMQX containerized broker for message brokering
- **Database**: PostgreSQL for persistent storage of sensor data, alerts, and IoT metadata
- **Data Models**: ORM models for Sensors, Readings, Alerts, Warehouses, Exploitations, Countries, and Lots
- **Serial Communication**: Read data from IoT devices via serial ports
- **Environment Configuration**: Flexible configuration via `.env` file

## Prerequisites

- Windows, Linux, or macOS
- Docker and Docker Compose (for running EMQX and PostgreSQL)
- Python 3.9 or higher
- A terminal (PowerShell, CMD, Bash)
- An MQTT client for testing (EMQX MQTTX Web view or `mqttx` CLI)

## Quick Start

### 1. Clone the repository

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
MQTT_TOPIC=sensors/readings

# Serial Port Configuration
PORT_SERIES=/dev/ttyUSB0  # On Windows: COM3, etc.
BAUD_RATE=9600

# Database Configuration
DB_URL=postgresql://postgres:postgres@localhost:5432/iot_data
```

### 4. Start Docker services

Ensure Docker and Docker Compose are installed, then run:

```bash
docker-compose up -d
```

This will start:
- **EMQX Broker** on port `1883` (MQTT) and `18083` (Web Console)
- **PostgreSQL** on port `5432`

### 5. Initialize the database

```bash
python main.py
```

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
├── main.py                  # Application entry point
├── mqtt.py                  # MQTT client and message handling
├── database.py              # Database setup and session management
├── docker-compose.yml       # Docker services configuration (EMQX, PostgreSQL)
├── pyproject.toml          # Python project metadata and dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
└── models/                 # SQLAlchemy ORM models
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
| `MQTT_TOPIC` | Topic for publishing sensor data | `sensors/readings` |
| `PORT_SERIES` | Serial port for sensor data input | `/dev/ttyUSB0` or `COM3` |
| `BAUD_RATE` | Serial port baud rate | `9600` |
| `DB_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:5432/db` |

### Docker Services

**EMQX Configuration:**
- Default admin credentials: `admin` / `public`
- MQTT port: `1883`
- WebSocket port: `8083`
- Secure port: `8084`
- Web console: `http://localhost:18083`

**PostgreSQL Configuration:**
- Default user: `postgres`
- Default password: `postgres`
- Default database: `iot_data`
- Port: `5432`

## Data Models

The application manages the following entities:

- **IotSensor**: Represents connected IoT sensors with metadata
- **SensorReading**: Records measurements from sensors (temperature, humidity, etc.)
- **Alerte**: Stores alerts triggered by sensor values
- **Exploitation**: Represents farms or production facilities
- **Warehouse**: Storage facility information
- **Lot**: Batch or production lot tracking
- **Country**: Geographic location data

## Core Components

### main.py
Application entry point that initializes the database and starts the MQTT client.

### mqtt.py
Handles MQTT client connection, subscribes to sensor topics, and processes incoming messages.

### database.py
Manages PostgreSQL connection using SQLAlchemy ORM.

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
psql -h localhost -U postgres -d iot_data
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
