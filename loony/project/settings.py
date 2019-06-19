import logging
import os
import sys

from alchemysession import AlchemySessionContainer


# Get everything from environment
# Telegram credentials
API_ID = os.getenv("API_ID", None)
API_HASH = os.getenv("API_HASH", None)

# Database connectivity information
DIALECT = os.getenv("DIALECT", None)
DB_USER = os.getenv("DB_USER", None)
DB_PASS = os.getenv("DB_PASS", None)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_DATA", None)

try:
    container = AlchemySessionContainer(
        f"{DIALECT}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
except ValueError:
    logging.fatal("Can't connect to the database, check your environment!")
    sys.exit(1)
