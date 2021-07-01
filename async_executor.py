import asyncio
import logging

import requests

from EventToInternet.KeyboardListener import KeyboardListener

# set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="/etc/systemd/system/EventToInternet.log",
    format="%(levelname)s (%(asctime)s): %(message)s",
)

API_ENDPOINT = "http://127.0.0.1:8080/api/hid_event"


class HidEventListener(KeyboardListener):
    """listen to a barcode and RFID reader in the background"""

    async def dict_handler(self, dict_event: dict) -> None:
        """handle RFID or barcode scan event and post data to a Rest API endpoint"""

        logging.debug(f"Handling event:\n{dict_event}")

        requests.post(
            url=API_ENDPOINT,
            json=dict_event
        )

        logging.info(f"Event relayed to endpoint {API_ENDPOINT}")


# start the daemon
if __name__ == "__main__":
    # initialize an instance of the class
    HidEventListener()

    # run an endless async process
    loop = asyncio.get_event_loop()
    loop.run_forever()
