import asyncio
import typing as tp
from dataclasses import dataclass, field
from datetime import datetime

import evdev
from loguru import logger

from EventToInternet import (
    KEYBOARD_MAX_STRING_LENGTH,
    KEYBOARD_UPDATE_DEVICES_TIMEOUT,
    _config_event_to_string as cfg,
)

# Type annotations
EventDict = tp.Dict[str, tp.Union[str, tp.Dict[str, str]]]


@dataclass
class KeyboardListener:
    regular_letters_codes: tp.Dict[int, str] = field(
        default_factory=lambda: field(default_factory=lambda: cfg.regular_letters_codes.copy())
    )
    regular_symbols_codes: tp.Dict[int, str] = field(default_factory=lambda: cfg.regular_symbols_codes.copy())
    capital_letters_codes: tp.Dict[int, str] = field(default_factory=lambda: cfg.capital_letters_codes.copy())
    capital_symbols_codes: tp.Dict[int, str] = field(default_factory=lambda: cfg.capital_symbols_codes.copy())
    numpad_symbols_codes: tp.Dict[int, str] = field(default_factory=lambda: cfg.numpad_symbols_codes.copy())
    send_trigger_keys: tp.Set[str] = field(default_factory=lambda: cfg.send_trigger_keys.copy())
    capitalize_all_keys: tp.Set[str] = field(default_factory=lambda: cfg.capitalize_all_keys.copy())
    capitalize_symbols_turn_keys: tp.Set[str] = field(default_factory=lambda: cfg.capitalize_symbols_turn_keys.copy())
    memory_devices: tp.Dict[tp.Any, tp.Any] = field(default_factory=dict)
    event_devices: tp.Dict[tp.Any, tp.Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        devices = map(evdev.InputDevice, evdev.list_devices())
        self.event_devices = {dev.path: dev for dev in devices}

        asyncio.ensure_future(self._update_devices())
        for device in self.event_devices.values():
            asyncio.ensure_future(self._get_keyboard_events(device))

    async def _update_devices(self) -> None:
        while True:
            await asyncio.sleep(KEYBOARD_UPDATE_DEVICES_TIMEOUT)
            new_event_devices = set(evdev.list_devices())
            old_event_devices = set(self.event_devices.keys())
            add_event_devices = new_event_devices.difference(old_event_devices)
            remove_event_devices = old_event_devices.difference(new_event_devices)
            if len(add_event_devices) > 0:
                for device in add_event_devices:
                    self.event_devices[device] = evdev.InputDevice(device)
                    asyncio.create_task(self._get_keyboard_events(self.event_devices[device]))
            if len(remove_event_devices) > 0:
                for device in remove_event_devices:
                    self.event_devices.pop(device)
                    try:
                        self.memory_devices.pop(device)
                    except KeyError:
                        pass

    async def _get_keyboard_events(self, device) -> None:
        try:
            async for event in device.async_read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    category = evdev.categorize(event)
                    if type(category.keycode) == list:
                        continue
                    try:
                        await self._keyboard_event_handler(device, category)
                    except Exception as e:
                        logger.error(
                            "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args)
                        )
        except OSError as e:
            if e.errno == 19:
                return

    async def _keyboard_event_handler(self, device, category) -> None:
        if self.memory_devices.get(device.path) is None:
            self.memory_devices[device.path] = {
                "string": "",
                "is_capital_letters": False,
                "is_capital_symbols": False,
            }
        if len(self.memory_devices.get(device.path)["string"]) > KEYBOARD_MAX_STRING_LENGTH:
            self.memory_devices[device.path]["string"] = self.memory_devices[device.path]["string"][1:]
        if category.keystate == category.key_hold:
            return
        if category.keycode in self.send_trigger_keys:
            if len(self.memory_devices[device.path]["string"]) > 0:
                json_event: EventDict = {
                    "string": self.memory_devices[device.path]["string"],
                    "name": device.name,
                    "timestamp": str(datetime.timestamp(datetime.now())),
                    "info": {
                        "phys": device.phys,
                        "path": device.path,
                        "fd": device.fd,
                        "bustype": device.info.bustype,
                        "product": device.info.product,
                        "vendor": device.info.vendor,
                        "version": device.info.version,
                    },
                }
                await self.dict_handler(json_event)
                self.memory_devices[device.path]["string"] = ""
            return
        if category.keycode in self.capitalize_all_keys:
            if category.keystate in [category.key_down, category.key_up]:
                self.memory_devices[device.path]["is_capital_letters"] = not self.memory_devices[device.path][
                    "is_capital_letters"
                ]
                self.memory_devices[device.path]["is_capital_symbols"] = not self.memory_devices[device.path][
                    "is_capital_symbols"
                ]
        elif category.keycode in self.capitalize_symbols_turn_keys and category.keystate == category.key_down:
            self.memory_devices[device.path]["is_capital_letters"] = not self.memory_devices[device.path][
                "is_capital_letters"
            ]
        if category.keystate != category.key_down:
            return
        if (
            self.memory_devices[device.path]["is_capital_letters"]
            and category.scancode in self.capital_letters_codes.keys()
        ):
            self.memory_devices[device.path]["string"] += self.capital_letters_codes.get(category.scancode)
        elif (
            not self.memory_devices[device.path]["is_capital_letters"]
            and category.scancode in self.regular_letters_codes.keys()
        ):
            self.memory_devices[device.path]["string"] += self.regular_letters_codes.get(category.scancode)
        elif (
            self.memory_devices[device.path]["is_capital_symbols"]
            and category.scancode in self.capital_symbols_codes.keys()
        ):
            self.memory_devices[device.path]["string"] += self.capital_symbols_codes.get(category.scancode)
        elif (
            not self.memory_devices[device.path]["is_capital_symbols"]
            and category.scancode in self.regular_symbols_codes.keys()
        ):
            self.memory_devices[device.path]["string"] += self.regular_symbols_codes.get(category.scancode)
        elif category.scancode in self.numpad_symbols_codes.keys():
            self.memory_devices[device.path]["string"] += self.numpad_symbols_codes.get(category.scancode)

    async def dict_handler(self, event_dict: EventDict) -> None:
        logger.debug(event_dict)
