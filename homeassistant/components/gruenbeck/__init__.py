"""The gruenbeck-sc18 integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .gruenbeck import GruenbeckPolling

_LOGGER = logging.getLogger(__name__)


# List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """hass.states.async_set("hello_state.world", "Paulus")."""
    _LOGGER.warning("__init__ async_setup %s", config.get("gruenbeck"))
    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up gruenbeck-sc18 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    # 1. Create API instance
    # 2. Validate the API connection (and authentication)
    # 3. Store an API object for your platforms to access
    gbr = GruenbeckPolling(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = gbr
    _LOGGER.warning("__init__ async_setup_entry %s", entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.warning("__init__ async_unload_entry")
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
