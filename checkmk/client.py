"""
MIT License

Copyright (c) 2025-present tom-jm69

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
from typing import List

from .exceptions import HostParseError, ServiceParseError
from .host import Host
from .http import CheckmkHTTP
from .service import Service
from .state import ConnectionState

__all__ = ("Client",)


_log = logging.getLogger(__name__)


class Client:
    """
    Async client for the Checkmk REST API.
    """

    def __init__(
        self,
        url: str,
        verify_ssl: bool,
        site_name: str,
        username: str,
        secret: str,
        api_version: str = "1.0",
        timeout: int = 30,
        retries: int = 5,
        port: int = 443,
        scheme: str = "https",
    ) -> None:
        """
        Initialize the Checkmk client, compute base endpoints, and set auth headers.

        Args:
            url: Checkmk hostname or IP (no scheme).
            verify_ssl: Verify SSL certificates.
            site_name: Checkmk site name.
            username: Username for authentication.
            secret: Password or API secret.
            api_version: Checkmk REST API version (e.g., `"1.0"`).
            timeout: Request timeout in seconds (default: `30`).
            retries: Retry count for polling attempts (default: `5`).
            port: Server port (default: `443`).
            scheme: Connection scheme, `"http"` or `"https"` (default: `"https"`).

        """
        self.url = url
        self.port = port
        self.scheme = scheme
        self.site_name = site_name
        self.base_url = f"{scheme}://{url}:{port}/{site_name}/check_mk"
        self.http = CheckmkHTTP(
            url=f"{self.base_url}/api/{api_version}/",
            username=username,
            secret=secret,
            verify_ssl=verify_ssl,
            timeout=timeout,
            retries=retries,
        )
        self._state = ConnectionState(self.http)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            _log.error(f"Exception occurred: {exc_val}")
        await self.close()
        return False

    def _set_api_key(self, *, api_key: str) -> None:
        """
        Set the API key for authentication.

        Args:
            api_key: The API key to use for authentication.
        """
        self.http.set_api_key(api_key)

    async def close(self) -> None:
        """*coroutine*
        Closes the `aiohttp.ClientSession`.
        """
        await self.http.close()

    async def get_services(self) -> List[Service]:
        """
        Fetch and deserialize all services from the Checkmk API.

        Returns:
            List[Service]: List of services.

        Raises:
            ServiceFetchError: On failed service request.
            ServiceParseError: On invalid response structure.
        """
        services = await self.http.get_services()

        parsed_services = []
        for service_data in services["value"]:
            try:
                service = Service(**service_data, state=self._state)
                parsed_services.append(service)
            except Exception as e:
                service_id = service_data.get("id", "unknown")
                raise ServiceParseError(
                    message=f"Parsing failed: {e}",
                    raw_data=service_data,
                    service_description=service_id,
                ) from e

        return parsed_services

    async def get_hosts(self) -> List[Host]:
        """
        Fetch and deserialize all hosts from the Checkmk API.

        Returns:
            List[Host]: List of hosts.

        Raises:
            HostFetchError: On failed host request.
            HostParseError: On invalid response structure.
        """
        hosts = await self.http.get_hosts()

        parsed_hosts = []
        for host_data in hosts["value"]:
            try:
                host = Host(**host_data, state=self._state)
                parsed_hosts.append(host)
            except Exception as e:
                host_name = host_data.get("id", "unknown")
                raise HostParseError(
                    message=f"Parsing failed: {e}", raw_data=host_data, host_name=host_name
                ) from e

        return parsed_hosts
