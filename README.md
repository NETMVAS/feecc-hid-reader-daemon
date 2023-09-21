# Feecc HID Reader Daemon

A lightweight Python daemon for sending USB peripheral events to a remote web server.

Sample code for sending all **keyboard** events to a web server [webhook.site](https://webhook.site/#!/595ddd9f-de34-4af8-845c-c52bb2614083):

```python
import asyncio
import requests
from EventToInternet.KeyboardListener import KeyboardListener


class BarcodeKeyboardListener(KeyboardListener):
    async def dict_handler(self, dict_event):
        print(dict_event)
        requests.post("https://webhook.site/595ddd9f-de34-4af8-845c-c52bb2614083", json=dict_event)


BarcodeKeyboardListener()

loop = asyncio.get_event_loop()
loop.run_forever()
```

## Technology Stack

* Operating system — [GNU/LINUX](https://www.gnu.org/) ([Ubuntu](https://ubuntu.com/) recommended)
* Language — [Python](https://www.python.org/)
* Service — [Systemd](https://manpages.ubuntu.com/manpages/xenial/en/man5/systemd.service.5.html)

## Features

- All code is asynchronous (even within the same thread it can work in parallel).
- Each USB device is recognized and monitored independently, allowing to connect any number of devices.
- The system supports connecting and disconnecting devices during operation, adjusting to them automatically.
- Since Python 3 is used, this allows to use this code on almost every Linux device with a minimum of steps to set up the project. 
- The system recognizes any device that can be read as a **USB keyboard**, including **barcode scanners**.
- The system is able to send numbers, letters and symbols of the English alphabet, typed in **upper and lower case**, and **Numpad symbols**.
- The system monitors pressing **LSHIFT** and **RSHIFT**, when changing the layout, as well as **CAPSLOCK** individually for each device. This keys are customizable.
- The universal character encoding **ASCII** is used, but **encoding is configurable**.
- The message is sent by pressing the **ENTER** or **NUMPAD ENTER** key (the keys are customizable).
- The individual message buffer is limited to **128** characters **(length configurable)**, and once it overflows, the memory for that input device will hold the last **128** characters typed.
- The system collects and displays additional information about the device to identify it and analyze traffic.

## Installation

```bash
git clone https://github.com/Multi-Agent-io/feecc-hid-reader-daemon.git
cd feecc-hid-reader-daemon
sudo docker-compose up -d --build
```

## Uninstallation

```bash
sudo bash /etc/systemd/system/feecc-hid-reader-daemon/uninstall.sh

sudo rm -rf /etc/systemd/system/feecc-hid-reader-daemon*
```

## Configuration

The file **EventToInternet/\_\_init\_\_.py** contains constants for working with USB peripherals.

```python
"""
    The maximum length of the string in characters.
    If a string longer than {KEYBOARD_MAX_STRING_LENGTH} characters is entered, 
    then the old characters of the message string will be erased and the system 
    will only remember the last {KEYBOARD_MAX_STRING_LENGTH} characters.
"""
KEYBOARD_MAX_STRING_LENGTH = 128  # 128 - Maximum barcode length according to GS1-128

"""
    The period of automatic updating of the list of all connected USB devices in seconds.
    Every {KEYBOARD_UPDATE_DEVICES_TIMEOUT} the system will check if a new keyboard or 
    scanner has been connected via the USB port.
"""
KEYBOARD_UPDATE_DEVICES_TIMEOUT = 1.0  # Scanner startup time is 3 seconds, so waiting another 1 second beyond that is acceptable
```

The file **EventToInternet/\_config\_event\_to\_string.py** contains  the selected encoding for interpreting  **keyboard events** like **characters** and lists of **capitalize** and **send** trigger keys.

```python
# Lower case letters encoding
regular_letters_codes = {
    16: u'q', 17: u'w', 18: u'e', 19: u'r', 20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 30: u'a',
    31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 44: u'z', 45: u'x', 46: u'c',
    47: u'v', 48: u'b', 49: u'n', 50: u'm',
}

# Lower case character encoding
regular_symbols_codes = {
    2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8', 10: u'9', 11: u'0', 12: u'-', 13: u'=',
    26: u'[', 27: u']', 39: u';', 40: u'\'', 41: u'`', 43: u'\\', 51: u',', 52: u'.', 53: u'/', 57: u' '
}

# Upper case letters encoding
capital_letters_codes = {
    16: u'Q', 17: u'W', 18: u'E', 19: u'R', 20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 30: u'A',
    31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 44: u'Z', 45: u'X', 46: u'C',
    47: u'V', 48: u'B', 49: u'N', 50: u'M',
}

# Upper case character encoding
capital_symbols_codes = {
    2: u'!', 3: u'@', 4: u'#', 5: u'$', 6: u'%', 7: u'^', 8: u'&', 9: u'*', 10: u'(', 11: u')', 12: u'_', 13: u'+',
    26: u'{', 27: u'}', 39: u':', 40: u'\"', 41: u'~', 43: u'|', 51: u'<', 52: u'>', 53: u'?', 57: u' ',
}

# Encoding of numpad keys
numpad_symbols_codes = {
    79: u'1', 80: u'2', 81: u'3', 75: u'4', 76: u'5', 77: u'6', 71: u'7', 72: u'8', 73: u'9', 82: u'0', 98: u'/',
    55: u'*', 74: u'-', 78: u'+', 83: u'.'
}

# Keys-triggers for sending a message. When this key is pressed, the current version of the message is sent, 
# after which the string is reset to zero, and the device again waits for data input. 
send_trigger_keys = {"KEY_ENTER", "KEY_KPENTER"}

# Keys for temporarily change of the capitalization.
# Usually it is the Shift key.
capitalize_all_keys = {"KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"}

# Keys for a fixed change of the capitalization. Usually it is the CapsLock key.
capitalize_symbols_turn_keys = {"KEY_CAPSLOCK", }
```