import asyncio
import os
import re

import requests
from loguru import logger

from EventToInternet.KeyboardListener import EventDict, KeyboardListener
from EventToInternet.logging_config import CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG

# apply logging configuration
logger.configure(handlers=[CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG])

API_RFID_ENDPOINT = os.getenv("HID_EVENT__RFID_ENDPOINT", "http://127.0.0.1:5001/employee/handle-rfid-event")
API_BARCODE_ENDPOINT = os.getenv("HID_EVENT__BARCODE_ENDPOINT", "http://127.0.0.1:5001/workbench/handle-barcode-event")


def is_a_ean13_barcode(string: str) -> bool:
    """define if the barcode scanner input is a valid EAN13 barcode"""
    return bool(re.fullmatch(r"\d{13}", string))


def identify_sender(event_dict: EventDict) -> EventDict:
    known_hid_devices: dict[str, str] = {
        "rfid_reader": os.getenv("HID_DEVICES__RFID_READER", "Sample"),
        "barcode_reader": os.getenv("HID_DEVICES__BARCODE_READER", "Sample"),
    }
    for sender_name, device_name in known_hid_devices.items():
        if device_name == event_dict["name"]:
            if sender_name == "barcode_reader" and not is_a_ean13_barcode(event_dict["string"]):
                logger.warning(f"{event_dict['string']} is not a EAN13 barcode and cannot be an internal unit ID.")
                return event_dict

            event_dict["name"] = sender_name
    return event_dict


class HidEventListener(KeyboardListener):
    """listen to a barcode and RFID reader in the background"""

    async def dict_handler(self, event_dict: EventDict) -> None:
        """handle RFID or barcode scan event and post data to a Rest API endpoint"""
        logger.debug(f"Handling event: {event_dict}")
        event_dict = identify_sender(event_dict)
        match event_dict["name"]:
            case "rfid_reader":
                logger.debug(f'Handling RFID event. String: {event_dict["string"]}')
                requests.post(url=API_RFID_ENDPOINT, json=event_dict)
                logger.info(f"Event relayed to endpoint {API_RFID_ENDPOINT}")
            case "barcode_reader":
                logger.debug(f'Handling barcode event. String: {event_dict["string"]}')
                requests.post(url=API_BARCODE_ENDPOINT, json=event_dict)
                logger.info(f"Event relayed to endpoint {API_BARCODE_ENDPOINT}")
            case _:
                logger.warning(f'Unknown device: {event_dict["name"]}.')


if __name__ == "__main__":
    HidEventListener()
    loop = asyncio.get_event_loop()
    loop.run_forever()
