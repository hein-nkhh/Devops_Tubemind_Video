import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# from core import process_message # run local
from src.core import process_message # run in docker

from libs.common.redis_client import redis_client
from libs.common.constants import QUEUE_NOTIFIER
from libs.common.logger import get_logger

logger = get_logger("notifier-main")

def run_notifier():
    logger.info("Notifier service started...")

    while True:
        try:
            message = redis_client.wait_for_task(QUEUE_NOTIFIER, timeout=5)

            if message:
                process_message(message)
            else:
                time.sleep(1)

        except Exception as e:
            logger.error("[Notifier] Worker error: %s", e)
            time.sleep(3)


if __name__ == "__main__":
    run_notifier()
