import os

# subscriber.py lit DB_URL au chargement du module (avant toute connexion réelle,
# create_engine est lazy) : on fournit une valeur factice pour permettre l'import en CI.
os.environ.setdefault("DB_URL", "postgresql+psycopg://test:test@localhost:5432/test")
