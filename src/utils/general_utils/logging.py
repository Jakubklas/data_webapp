import logging
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S"
))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_msg(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        now = datetime.now().strftime("%H:%M:%S")
        logger.info(f"\a⏳ Starting {func.__name__}")
        result = func(self, *args, **kwargs)
        return result
    return wrapper
