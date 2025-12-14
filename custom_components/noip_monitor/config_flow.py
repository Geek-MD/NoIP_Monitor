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

    def __init__(self) -> None:
        """Initialize the config flow."""
        # Store credentials temporarily during multi-step flows
        self._username: str | None = None
        self._password: str | None = None

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
                valid, _requires_2fa = await client.async_validate_auth()
                await client.close()
                
                # Note: If 2FA is detected, we inform the user in the error message
                # NoIP doesn't support TOTP codes in API requests, so users must
                # use application-specific passwords
                if _requires_2fa:
                    errors["base"] = "2fa_required"
                elif valid:
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
