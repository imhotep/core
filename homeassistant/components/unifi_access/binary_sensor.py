"""Platform for sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .hub import UnifiAccessCoordinator, UnifiAccessHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Binary Sensor for passed config entry."""
    hub: UnifiAccessHub = hass.data[DOMAIN][config_entry.entry_id]

    coordinator = UnifiAccessCoordinator(hass, hub)

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        UnifiDoorStatusEntity(coordinator, key)
        for key, value in coordinator.data.items()
    )


class UnifiDoorStatusEntity(CoordinatorEntity, BinarySensorEntity):
    """Unifi Access DPS Entity."""

    should_poll = False

    def __init__(self, coordinator, door_id) -> None:
        """Initialize DPS Entity."""
        super().__init__(coordinator, context=door_id)
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self.id = door_id
        self.door = self.coordinator.data[door_id]
        self._attr_unique_id = self.door.id
        self.device_name = self.door.name
        self._attr_name = f"{self.door.name} Door Position Sensor"
        self._attr_available = self.door.door_position_status is not None
        self._attr_is_on = self.door.door_position_status == "open"

    @property
    def device_info(self) -> DeviceInfo:
        """Get device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.door.id)},
            name=self.door.name,
            model="UAH",
            manufacturer="Unifi",
        )

    @property
    def is_open(self) -> bool:
        """Get door status."""
        return self.door.is_open

    def _handle_coordinator_update(self) -> None:
        """Handle updates in case of polling."""
        self._attr_is_on = self.door.is_open
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle updates in case of push."""
        await super().async_added_to_hass()
        self.door.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Handle updates in case of push and removal."""
        await super().async_will_remove_from_hass()
        self.door.remove_callback(self.async_write_ha_state)
