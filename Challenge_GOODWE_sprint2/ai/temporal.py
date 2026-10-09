from datetime import datetime

from config import ZONE


def local_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(ZONE)
