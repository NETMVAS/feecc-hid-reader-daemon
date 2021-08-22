import asyncio
import logging

import requests

from EventToInternet.KeyboardListener import KeyboardListener, EventDict

# set up logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s (%(asctime)s): %(message)s")

API_ENDPOINT = "http://127.0.0.1:8080/api/hid_event"


class HidEventListener(KeyboardListener):
    """listen to a barcode and RFID reader in the background"""

    async def dict_handler(self, event_dict: EventDict) -> None:
        """handle RFID or barcode scan event and post data to a Rest API endpoint"""
        logging.debug(f"Handling event: {event_dict}")
        requests.post(url=API_ENDPOINT, json=event_dict)
        logging.info(f"Event relayed to endpoint {API_ENDPOINT}")


if __name__ == "__main__":
    HidEventListener()
    loop = asyncio.get_event_loop()
    loop.run_forever()
