"""Example integration using DataUpdateCoordinator."""
from datetime import datetime, timedelta
import logging

import async_timeout

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .gruenbeck import ApiError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Config entry example."""
    # assuming API object stored here by __init__.py
    _LOGGER.warning("Sensor.py async_setup %s", entry.data)
    my_api = hass.data[DOMAIN][entry.entry_id]
    coordinator = MyCoordinator(hass, my_api, entry.data)
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    # coordinator.
    # coordinator.data = ["apple", "banana", "cherry"]
    # data = [MyEntity, MyEntity]
    # await coordinator.async_config_entry_first_refresh()
    async_add_entities(
        # [ MyEntity(coordinator, idx) for idx, ent in enumerate([1]),
        [
            CapacityEntity(coordinator),
            TimeEntity(coordinator),
            ActualFlowEntity(coordinator),
            TimeSinceLastRegenerationEntity(coordinator),
            TimeLeftRegenerationStep(coordinator),
            PercentRegeneration(coordinator),
            RegenerationStepName(coordinator),
        ],
        # update_before_add=True
        # MyEntity(coordinator, idx)
        # for idx, ent in enumerate(data)
    )


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, my_api, entryData) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="GruenbeckCoordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=entryData["interval"]),
        )
        self.my_api = my_api
        _LOGGER.warning("MyCoordinator: %s", entryData)

    def get_abc(self, item: str):
        """Testfunktion."""
        return self.my_api.get_item(item)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.warning("Async_update_data called")
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(30):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                listening_idx = set(self.async_contexts())
                return await self.my_api.fetch_data(listening_idx)
            # except ApiAuthError as err:
        except ApiError as err:
            # print("Exception caught")
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")


class MyEntity(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity. The CoordinatorEntity class provides: should_poll async_update async_added_to_hass available."""

    def __init__(self, coordinator, idx) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning(
            "MyEntity _handle_coordinator_update Restkapazität %s",
            self.coordinator.get_abc("D_A_1_2"),
        )
        # self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()


class CapacityEntity(CoordinatorEntity, SensorEntity):
    """Docstring."""

    _attr_device_clas = SensorDeviceClass.VOLUME

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
        self._attr_name = "Restkapazität"
        self._attr_unique_id = "sensor.remainingcapacity"
        self._attr_icon = "mdi:arrow-expand-vertical"
        self._attr_device_class = SensorDeviceClass.WATER

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("CapacityEntity _handle_coordinator_update")
        try:
            self._attr_native_value = self.coordinator.get_abc("D_A_1_2")
            self.async_write_ha_state()
        except KeyError:
            # print("Keine Daten")
            logging.warning("Keine Daten")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class ActualFlowEntity(CoordinatorEntity, SensorEntity):
    """Docstring."""

    _attr_device_clas = SensorDeviceClass.VOLUME

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_native_unit_of_measurement = UnitOfVolume.LITERS
        self._attr_name = "Aktueller Durchfluss"
        self._attr_unique_id = "sensor.actualflow"
        self._attr_icon = "mdi:swap-vertical"
        self._attr_device_class = SensorDeviceClass.WATER

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("ActualFlowEntity _handle_coordinator_update")
        try:
            self._attr_native_value = self.coordinator.get_abc("D_A_1_1")
            self.async_write_ha_state()
        except KeyError:
            _LOGGER.warning("Keine Daten")
            # print("Keine Daten")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class TimeSinceLastRegenerationEntity(CoordinatorEntity, SensorEntity):
    """Docstring."""

    _attr_device_clas = SensorDeviceClass.DURATION

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_native_unit_of_measurement = "h"
        self._attr_name = "Zeit seit letzer Regeneration"
        self._attr_unique_id = "sensor.timesincelastregeneration"
        self._attr_icon = "mdi:progress-clock"
        self._attr_device_class = SensorDeviceClass.DURATION

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("TimeSinceLastRegenerationEntity _handle_coordinator_update")
        try:
            self._attr_native_value = self.coordinator.get_abc("D_A_3_1")
            self.async_write_ha_state()
        except KeyError:
            _LOGGER.warning("Keine Daten")
            # print("Keine Daten")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class PercentRegeneration(CoordinatorEntity, SensorEntity):
    """Docstring."""

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_native_unit_of_measurement = "%"
        self._attr_name = "Prozentsatz der laufenden Regeneration"
        self._attr_unique_id = "sensor.softener_percent_regeneration"
        self._attr_icon = "mdi:refresh-auto"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            self._attr_native_value = self.coordinator.get_abc("D_A_3_2")
            self.async_write_ha_state()
        except KeyError:
            pass

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class TimeLeftRegenerationStep(CoordinatorEntity, SensorEntity):
    """Docstring."""

    _attr_device_clas = SensorDeviceClass.DURATION

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_native_unit_of_measurement = "min"
        self._attr_name = "Restdauer aktueller Regenerationsschritt"
        self._attr_unique_id = "time_left_regeneration_step"
        self._attr_icon = "mdi:progress-clock"
        self._attr_device_class = SensorDeviceClass.DURATION

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("TimeLeftRegenerationStep _handle_coordinator_update")
        try:
            self._attr_native_value = self.coordinator.get_abc("D_A_2_1")
            self.async_write_ha_state()
        except KeyError:
            _LOGGER.warning("Keine Daten")
            # print("Keine Daten")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class RegenerationStepName(CoordinatorEntity, SensorEntity):
    """Docstring."""

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_name = "Regnerationsschritt"
        self._attr_unique_id = "regeneration_step_name"
        self._attr_icon = "mdi:debug-step-over"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        dictionary = {
            0: "keine Regeneration",
            1: "Soletank füllen",
            2: "Besalzen",
            3: "Verdrängen",
            4: "Rückspülen",
            5: "Auswaschen",
        }
        try:
            self._attr_native_value = dictionary.get(
                int(self.coordinator.get_abc("D_Y_5"))
            )
            self.async_write_ha_state()
        except KeyError:
            _LOGGER.warning("Keine Daten")
            # print("Keine Daten")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )


class TimeEntity(CoordinatorEntity, SensorEntity):
    """Testklasse, zeigt nur die Uhrzeit des letzten Aufrufs an."""

    _attr_device_clas = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        self._attr_available = False  # This overrides the default
        self._attr_name = "Datum/Uhrzeit"
        self._attr_unique_id = "sensor.datatime"
        self._attr_icon = "mdi:clock"
        # self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.warning("TimeEntity _handle_coordinator_update")
        # self._attr_native_value = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

        # print(datetime.utcnow(tz=TZ1()).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
        self._attr_native_value = (
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
        )
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "1234")
            },
            name=self.name,
            manufacturer="Grünbeck",
            model="SC18",
            sw_version="V1.1",
            via_device=(DOMAIN, ""),
        )
