import os
import redis

from teleredis import RedisSession

API_ID = os.getenv("API_ID", None)
API_HASH = os.getenv("API_HASH", None)
GRACE = int(os.getenv("GRACE", 5))  # Minutes
DJANGO_EMAIL=os.getenv("DJANGO_EMAIL")
DJANGO_PASSWORD = os.getenv("DJANGO_PASSWORD")
DJANGO_USER = os.getenv("DJANGO_USER")
REDIS_SESSION_NAME = os.getenv("SESSION_NAME", "default")
REQUESTS_TIMEOUT = int(os.getenv("REQUESTS_TIMEOUT", 10))
REST_HOST = os.getenv("REST_HOST", "0.0.0.0")
REST_PORT = os.getenv("REST_PORT", "8000")
TOR_HOST = os.getenv("TOR_HOST", "0.0.0.0")
TOR_PORT = int(os.getenv("TOR_PORT", 9050))

redis_connector = redis.Redis(
    host=os.getenv("REDIS_HOST", "0.0.0.0"),
    port=os.getenv("REDIS_PORT", 6379),
    db=0,
    decode_responses=False,
)
session = RedisSession(REDIS_SESSION_NAME, redis_connector)
