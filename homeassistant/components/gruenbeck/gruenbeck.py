"""Polling Class for Gruenbeck."""
from datetime import datetime
import logging

import aiohttp

# import xml.etree.ElementTree as ET
# from defusedxml.ElementTree import parse
import defusedxml.ElementTree as ET

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ApiError(Exception):
    """Raised when an update has failed."""


class GruenbeckInitial:
    """Docstring Class."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        self.hass = hass
        self.dict: dict = {}
        self.host = "172.16.0.41"  # entry["host"]
        _LOGGER.warning("GruenbeckInitial: Host: %s", self.host)

    async def fetch_init_data(self) -> bool:
        """Fetch data from the device."""
        url = "http://" + self.host + "/mux_http"  # URL der Wasserenthaertungsanlage
        headers = {"Content-Type": "application/xml"}  # HTTP Post Header

        # POST Daten
        xml_akt = "id=626&show=D_C_1_1|D_Y_6|D_Y_7~"
        # POST
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url=url, data=xml_akt) as response:
                data = await response.text()
                # print(data)
                # <data><code>ok</code><D_C_1_1>0</D_C_1_1><D_Y_6>V01.01.02</D_Y_6><D_Y_7>-</D_Y_7></data>
        await session.close()

        if data == "":
            _LOGGER.warning("Leere Daten erhalten")
            return False
            # raise ApiError("Leere Daten erhalten") -> Setzt Entities auf Uunbekannt, wenn auslesefehler

        # Add missing header
        xml_header = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        xml_footer = ""

        xml_text = xml_header + data + xml_footer
        xml_text = xml_text.replace("<code>ok</code>", "")

        ET.fromstring(xml_text)
        # root = ET.fromstring(xml_text)
        # print("Version: " + root.find("D_Y_6").text)

        # self.add_item(root, "D_Y_5")

        _LOGGER.warning(
            "GBI Uhrzeit: %s", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        )
        return True


class GruenbeckPolling:
    """My custom gruenbeck_polling."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        self.hass = hass
        self.dict: dict = {}
        self.host = entry.data["host"]
        # _LOGGER.warning("GruenbeckPolling: Host: %s", entry.data["host"])

    def add_item(self, root, item: str):
        """Add Item to dictionary."""
        self.dict[item] = root.find(item).text

    def get_item(self, item: str) -> str:
        """Get Item from dictionary."""
        return self.dict[item]

    async def fetch_data(self, listening_idx) -> bool:
        """Fetch data from the device."""
        _LOGGER.warning("Fetch_data called %s", listening_idx)

        url = "http://" + self.host + "/mux_http"  # URL der Wasserenthaertungsanlage
        headers = {"Content-Type": "application/xml"}  # HTTP Post Header

        # POST Daten
        xml_akt = "id=626&show=D_Y_1|D_Y_5|D_Y_10_1|D_A_1_1|D_A_1_2|D_A_1_3|D_A_2_1|D_A_3_1|D_A_3_2~"
        _LOGGER.warning("HTTP-Post %s", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
        # POST
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url=url, data=xml_akt) as response:
                data = await response.text()
                # print(data)
        await session.close()

        if data == "":
            _LOGGER.warning("Leere Daten erhalten")
            return False
            # raise ApiError("Leere Daten erhalten") -> Setzt Entities auf Uunbekannt, wenn auslesefehler

        # Add missing header
        xml_header = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        xml_footer = ""

        xml_text = xml_header + data + xml_footer
        xml_text = xml_text.replace("<code>ok</code>", "")

        root = ET.fromstring(xml_text)

        self.add_item(root, "D_Y_5")
        # _LOGGER.warning("Aktueller Durchfluss: %s", root.find("D_A_1_1").text)
        self.add_item(root, "D_A_1_1")
        # _LOGGER.warning("Restkapazität: %s", root.find("D_A_1_2").text)
        self.add_item(root, "D_A_1_2")
        # _LOGGER.warning("Kapazitätszahl: %s", root.find("D_A_1_3").text)
        self.add_item(root, "D_A_1_3")
        # _LOGGER.warning(
        #    "Restzeit/-menge Reg.Schritt: %s", root.find("D_A_2_1").text
        # )
        self.add_item(root, "D_A_2_1")
        # _LOGGER.warning("Letzte Regeneration: %s", root.find("D_A_3_1").text)
        self.add_item(root, "D_A_3_1")
        # _LOGGER.warning("Über: %s", root.find("D_A_3_2").text)
        self.add_item(root, "D_A_3_2")

        _LOGGER.warning("Uhrzeit: %s", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
        return True
