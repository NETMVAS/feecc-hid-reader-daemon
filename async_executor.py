import asyncio
from loguru import logger

import requests

from EventToInternet.KeyboardListener import KeyboardListener, EventDict
from EventToInternet.logging import CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG

# apply logging configuration
logger.configure(handlers=[CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG])

API_ENDPOINT = "http://127.0.0.1:5000/workbench/hid-event"


class HidEventListener(KeyboardListener):
    """listen to a barcode and RFID reader in the background"""

    async def dict_handler(self, event_dict: EventDict) -> None:
        """handle RFID or barcode scan event and post data to a Rest API endpoint"""
        logger.debug(f"Handling event: {event_dict}")
        requests.post(url=API_ENDPOINT, json=event_dict)
        logger.info(f"Event relayed to endpoint {API_ENDPOINT}")


if __name__ == "__main__":
    HidEventListener()
    loop = asyncio.get_event_loop()
    loop.run_forever()
