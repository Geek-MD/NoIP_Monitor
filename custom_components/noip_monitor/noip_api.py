"""NoIP API Client."""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

NOIP_API_BASE_URL = "https://dynupdate.no-ip.com/nic/update"
NOIP_API_HOST_INFO = "https://www.noip.com/api/host"


class NoIPClient:
    """NoIP API Client."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize the NoIP client."""
        self.username = username
        self.password = password
        self._session: aiohttp.ClientSession | None = None

    def _get_auth_header(self) -> dict[str, str]:
        """Get authorization header."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_get_host_ip(self, hostname: str) -> dict[str, Any]:
        """Get IP address for a specific hostname."""
        try:
            session = await self._get_session()
            headers = self._get_auth_header()
            headers["User-Agent"] = "Home Assistant NoIP Monitor/1.0"
            
            # NoIP API uses a specific endpoint for checking status
            params = {
                "hostname": hostname,
                "myip": ""  # Empty to just check current IP
            }
            
            async with session.get(
                NOIP_API_BASE_URL,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                text = await response.text()
                _LOGGER.debug(f"NoIP response for {hostname}: {text}")
                
                # Parse NoIP response
                # Responses can be: "good <ip>", "nochg <ip>", "nohost", etc.
                if response.status == 200:
                    parts = text.strip().split()
                    if len(parts) >= 2 and parts[0] in ["good", "nochg"]:
                        ip_address = parts[1]
                        return {
                            "hostname": hostname,
                            "ip": ip_address,
                            "status": "connected",
                            "response": parts[0],
                        }
                    elif "nohost" in text:
                        return {
                            "hostname": hostname,
                            "ip": None,
                            "status": "disconnected",
                            "error": "Host not found",
                        }
                    elif "abuse" in text:
                        return {
                            "hostname": hostname,
                            "ip": None,
                            "status": "disconnected",
                            "error": "Account blocked for abuse",
                        }
                    elif "badauth" in text:
                        return {
                            "hostname": hostname,
                            "ip": None,
                            "status": "disconnected",
                            "error": "Invalid credentials",
                        }
                    else:
                        return {
                            "hostname": hostname,
                            "ip": None,
                            "status": "disconnected",
                            "error": f"Unknown response: {text}",
                        }
                else:
                    return {
                        "hostname": hostname,
                        "ip": None,
                        "status": "disconnected",
                        "error": f"HTTP {response.status}",
                    }
                    
        except asyncio.TimeoutError:
            _LOGGER.error(f"Timeout connecting to NoIP API for {hostname}")
            return {
                "hostname": hostname,
                "ip": None,
                "status": "disconnected",
                "error": "Timeout",
            }
        except Exception as err:
            _LOGGER.error(f"Error fetching NoIP data for {hostname}: {err}")
            return {
                "hostname": hostname,
                "ip": None,
                "status": "disconnected",
                "error": str(err),
            }

    async def async_get_hosts(self) -> dict[str, dict[str, Any]]:
        """Get all hosts from NoIP account."""
        # This is a simplified version - NoIP doesn't have a public API
        # to list all hosts, so we'll return empty and rely on user configuration
        return {}

    async def async_validate_auth(self) -> bool:
        """Validate authentication credentials."""
        try:
            # Try with a dummy hostname to check if credentials are valid
            session = await self._get_session()
            headers = self._get_auth_header()
            headers["User-Agent"] = "Home Assistant NoIP Monitor/1.0"
            
            async with session.get(
                NOIP_API_BASE_URL,
                headers=headers,
                params={"hostname": "test"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                text = await response.text()
                # If we get "badauth", credentials are invalid
                if "badauth" in text:
                    return False
                # Any other response means credentials are OK
                # (even "nohost" means auth worked)
                return True
                
        except Exception as err:
            _LOGGER.error(f"Error validating NoIP credentials: {err}")
            return False

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
