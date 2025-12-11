"""Sensor platform for NoIP Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATE_DISCONNECTED

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NoIP Monitor sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Wait for first data update
    await coordinator.async_config_entry_first_refresh()

    # Create sensors for each hostname
    entities = []
    if coordinator.data:
        for hostname in coordinator.data:
            entities.append(NoIPSensor(coordinator, entry, hostname))

    async_add_entities(entities)

    # Add listener to add new sensors when options change
    @callback
    def _async_add_remove_sensors() -> None:
        """Add or remove sensors based on coordinator data."""
        current_hostnames = set(coordinator.data.keys()) if coordinator.data else set()
        
        # Get existing sensor hostnames
        existing_entities = [
            entity for entity in hass.data[DOMAIN].get(f"{entry.entry_id}_entities", [])
        ]
        existing_hostnames = {entity.hostname for entity in existing_entities}

        # Add new sensors
        new_entities = []
        for hostname in current_hostnames - existing_hostnames:
            new_entities.append(NoIPSensor(coordinator, entry, hostname))
        
        if new_entities:
            async_add_entities(new_entities)
            if f"{entry.entry_id}_entities" not in hass.data[DOMAIN]:
                hass.data[DOMAIN][f"{entry.entry_id}_entities"] = []
            hass.data[DOMAIN][f"{entry.entry_id}_entities"].extend(new_entities)

    # Store initial entities
    if entities:
        hass.data[DOMAIN][f"{entry.entry_id}_entities"] = entities

    # Register coordinator listener
    entry.async_on_unload(coordinator.async_add_listener(_async_add_remove_sensors))


class NoIPSensor(CoordinatorEntity, SensorEntity):
    """Representation of a NoIP Monitor sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        hostname: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.hostname = hostname
        self._attr_unique_id = f"{entry.entry_id}_{hostname}"
        self._attr_name = hostname
        
        # Set device info to group all sensors under one device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"NoIP Monitor ({entry.data['username']})",
            "manufacturer": "NoIP",
            "model": "Dynamic DNS Monitor",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return STATE_DISCONNECTED

        host_data = self.coordinator.data.get(self.hostname)
        if not host_data:
            return STATE_DISCONNECTED

        if host_data.get("status") == "connected" and host_data.get("ip"):
            return host_data["ip"]
        
        return STATE_DISCONNECTED

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        host_data = self.coordinator.data.get(self.hostname, {})
        
        attributes = {
            "hostname": self.hostname,
            "status": host_data.get("status", "unknown"),
        }

        if host_data.get("response"):
            attributes["response"] = host_data["response"]
        
        if host_data.get("error"):
            attributes["error"] = host_data["error"]

        return attributes

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        if self.native_value == STATE_DISCONNECTED:
            return "mdi:lan-disconnect"
        return "mdi:lan-connect"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
