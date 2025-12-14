"""Config flow for NoIP Monitor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_HOSTNAMES, CONF_TOTP_CODE, DOMAIN
from .noip_api import NoIPClient

_LOGGER = logging.getLogger(__name__)


class NoIPConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for NoIP Monitor."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._username: str | None = None
        self._password: str | None = None
        self._requires_2fa: bool = False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Get credentials from user input
            username: str = user_input[CONF_USERNAME]
            password: str = user_input[CONF_PASSWORD]
            
            # Store credentials temporarily
            self._username = username
            self._password = password
            
            # Validate credentials
            client = NoIPClient(
                username=username,
                password=password,
            )
            
            try:
                valid, requires_2fa = await client.async_validate_auth()
                await client.close()
                
                if requires_2fa:
                    # Store that 2FA is required and move to 2FA step
                    self._requires_2fa = True
                    return await self.async_step_2fa()
                
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

    async def async_step_2fa(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the 2FA step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            totp_code = user_input[CONF_TOTP_CODE]
            
            # Check that we have username and password from previous step
            if not self._username or not self._password:
                return await self.async_step_user()
            
            # Validate credentials with 2FA code
            client = NoIPClient(
                username=self._username,
                password=self._password,
                totp_code=totp_code,
            )
            
            try:
                valid, _ = await client.async_validate_auth()
                await client.close()
                
                if valid:
                    # Create entry with unique ID based on username
                    await self.async_set_unique_id(self._username.lower())
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"NoIP ({self._username})",
                        data={
                            CONF_USERNAME: self._username,
                            CONF_PASSWORD: self._password,
                            CONF_TOTP_CODE: totp_code,
                        },
                    )
                else:
                    errors["base"] = "invalid_2fa"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during 2FA validation")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="2fa",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TOTP_CODE): str,
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
