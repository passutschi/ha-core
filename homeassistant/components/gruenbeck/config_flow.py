"""Config flow for gruenbeck-sc18 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .gruenbeck import GruenbeckInitial

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host", default="172.16.0.41"): str,
        # vol.Required("username"): str,
        # vol.Required("password"): str,
        vol.Required("interval", default=45): int,
    }
)


class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host
        _LOGGER.warning("Config_flow __init__")

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        _LOGGER.warning("Config_flow authenticate")
        return True


async def validate_input(hass: HomeAssistant, data) -> dict[str, Any]:
    """Validate the user input allows us to connect.Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user."""

    _LOGGER.warning("Config_flow validate input")
    # gbi = GruenbeckInitial(hass, data)
    # await gbi.fetch_init_data()

    # validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    gbi = GruenbeckInitial(hass, data)
    await gbi.fetch_init_data()

    # hub = PlaceholderHub(data["host"])

    # if not await hub.authenticate(data["username"], data["password"]):
    #    raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Grünbeck SC18 (" + data["host"] + ")"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for gruenbeck-sc18."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.warning("Config_flow async_step_user ----------------------------")
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

    _LOGGER.warning("Config_flow CannotConnect")


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

    _LOGGER.warning("Config_flow InvalidAuth")
