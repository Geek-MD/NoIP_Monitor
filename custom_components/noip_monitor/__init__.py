"""The NoIP Monitor integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .noip_api import NoIPClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

UPDATE_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NoIP Monitor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    client = NoIPClient(
        username=entry.data["username"],
        password=entry.data["password"],
        token_2fa=entry.data.get("2fa_token"),
    )

    # Create coordinator
    coordinator = NoIPDataUpdateCoordinator(hass, client, entry)
    
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class NoIPDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NoIP data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NoIPClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.client = client
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Update data via library."""
        try:
            hostnames = self.entry.options.get("hostnames", [])
            
            _LOGGER.debug("Updating NoIP data for hostnames: %s", hostnames)
            
            if not hostnames:
                # If no hostnames configured, try to get all from account
                _LOGGER.info("No hostnames configured. Please configure hostnames in integration options.")
                hostnames_data = await self.client.async_get_hosts()
                if hostnames_data:
                    _LOGGER.debug("Retrieved %d hosts from account", len(hostnames_data))
                    return hostnames_data
                _LOGGER.warning("No hostnames configured and unable to retrieve from account. Please configure hostnames manually.")
                return {}
            
            # Fetch data for configured hostnames
            data = {}
            for hostname in hostnames:
                _LOGGER.debug("Fetching data for hostname: %s", hostname)
                host_data = await self.client.async_get_host_ip(hostname)
                data[hostname] = host_data
                _LOGGER.debug("Data for %s: %s", hostname, host_data)
            
            _LOGGER.info("Successfully updated data for %d hostnames", len(data))
            return data
            
        except Exception as err:
            _LOGGER.error("Error communicating with NoIP API: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with NoIP API: {err}") from err
