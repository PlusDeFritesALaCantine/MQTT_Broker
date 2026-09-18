FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir paho-mqtt>=2.1.0 psycopg[binary]>=3.2.13 python-dotenv>=1.2.1 sqlalchemy>=2.0.49
COPY . .