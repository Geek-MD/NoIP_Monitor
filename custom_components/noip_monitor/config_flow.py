"""Config flow for NoIP Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HOSTNAMES, DOMAIN
from .noip_api import NoIPClient

_LOGGER = logging.getLogger(__name__)


class NoIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for NoIP Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Get credentials from user input
            username: str = user_input[CONF_USERNAME]
            password: str = user_input[CONF_PASSWORD]
            
            # Validate credentials
            client = NoIPClient(
                username=username,
                password=password,
            )
            
            try:
                valid = await client.async_validate_auth()
                await client.close()
                
                if valid:
                    # Create entry with unique ID based on username
                    await self.async_set_unique_id(username.lower())
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"NoIP ({username})",
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                        },
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during validation")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        entry: config_entries.ConfigEntry | None = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        
        if entry is None:
            return self.async_abort(reason="entry_not_found")
        
        if user_input is not None:
            # Get credentials from user input
            username: str = user_input[CONF_USERNAME]
            password: str = user_input[CONF_PASSWORD]
            
            # Validate credentials
            client = NoIPClient(
                username=username,
                password=password,
            )
            
            try:
                valid = await client.async_validate_auth()
                await client.close()
                
                if valid:
                    # Update the config entry with new credentials
                    self.hass.config_entries.async_update_entry(
                        entry,
                        data={
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                        },
                    )
                    # Reload the config entry to apply changes
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reconfigure_successful")
                else:
                    errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during reconfiguration")
                errors["base"] = "cannot_connect"

        # Show form with current username as suggested value
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        description={"suggested_value": entry.data.get(CONF_USERNAME, "")},
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> NoIPOptionsFlowHandler:
        """Get the options flow for this handler."""
        return NoIPOptionsFlowHandler(config_entry)


class NoIPOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for NoIP Monitor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Process comma-separated hostnames
            hostnames_input = user_input.get(CONF_HOSTNAMES, "")
            if hostnames_input:
                # Split by comma and clean up whitespace
                hostnames = [h.strip() for h in hostnames_input.split(",") if h.strip()]
            else:
                hostnames = []
            
            return self.async_create_entry(
                title="",
                data={CONF_HOSTNAMES: hostnames},
            )

        # Get current hostnames
        current_hostnames = self.config_entry.options.get(CONF_HOSTNAMES, [])
        hostnames_str = ", ".join(current_hostnames) if current_hostnames else ""

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_HOSTNAMES,
                        description={"suggested_value": hostnames_str},
                    ): str,
                }
            ),
            description_placeholders={
                "hostnames_example": "example.ddns.net, myhost.hopto.org"
            },
        )
