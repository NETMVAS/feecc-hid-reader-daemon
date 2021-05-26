import asyncio
import requests
from EventToInternet.KeyboardListener import KeyboardListener
import logging

# set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename="/etc/systemd/system/EventToInternet.log",
    format="%(asctime)s %(levelname)s: %(message)s"
)

API_ENDPOINT = "http://127.0.0.1:5000/api/hid_event"


class HidEventListener(KeyboardListener):
    """listen to a barcode and RFID reader in the background"""

    async def dict_handler(self, dict_event: dict) -> None:
        """handle RFID or barcode scan event and post data to a Rest API endpoint"""

        requests.post(
            url=API_ENDPOINT,
            json=dict_event
        )


# start the daemon
if __name__ == "__main__":

    # initialize an instance of the class
    HidEventListener()

    # run an endless async process
    loop = asyncio.get_event_loop()
    loop.run_forever()
