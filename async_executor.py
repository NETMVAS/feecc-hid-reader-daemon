import asyncio
import requests
from EventToInternet.KeyboardListener import KeyboardListener

API_ENDPOINT = "http://127.0.0.1:8080/api/rfid"


class RfidKeyboardListener(KeyboardListener):
    """listen to the R20D-USB-8H10D RFID reader in the background"""

    async def dict_handler(self, dict_event: dict) -> None:
        """handle RFID scan event and post data to a Rest API endpoint"""

        requests.post(
            url=API_ENDPOINT,
            json=dict_event
        )


# start the daemon
if __name__ == "__main__":

    # initialize an instance of the class
    RfidKeyboardListener()

    # run an endless async process
    loop = asyncio.get_event_loop()
    loop.run_forever()
