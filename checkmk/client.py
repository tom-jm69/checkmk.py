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

from .exceptions import ServiceFetchError, ServiceParseError
from .http import CheckmkHTTP
from .service import Service
from .host import Host
from .state import ConnectionState

__all__ = ("Client",)


_log = logging.getLogger(__name__)


class Client:
    """
    Async client for the Checkmk REST API.

    Extends `Wrapper` with Checkmk-specific endpoint construction and auth header
    configuration. Host/service caches are optional and managed by the subclass.

    Inherits session handling, logging, and background task management from `Wrapper`.
    """

    def __init__(
        self,
        url: str,
        verify_ssl: bool,
        site_name: str,
        username: str,
        secret: str,
        api_version: str,
        timeout=30,
        retries=5,
        port=443,
        scheme="http",
    ):
        """
        Initialize the Checkmk client, compute base endpoints, and set auth headers.

        Args:
            url: Checkmk hostname or IP (no scheme).
            verify_ssl: Verify SSL certificates.
            site_name: Checkmk site name.
            username: Username for authentication.
            secret: Password or API secret.
            api_version: Checkmk REST API version (e.g., `"1.0"`).
            hosts: Optional initial host cache (default: `None` → `[]`).
            services: Optional initial service cache (default: `None` → `[]`).
            timeout: Request timeout in seconds (default: `30`).
            retries: Retry count for polling attempts (default: `5`).
            port: Server port (default: `443`).
            scheme: Connection scheme, `"http"` or `"https"` (default: `"http"`).

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

    def set_api_key(self, *, api_key: str):
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
            List[Service] | None: List of services, or None on failure.

        Raises:
            ServiceFetchingError: On failed service request.
            ServiceParsingError: On invalid response structure.
        """
        try:
            services = await self.http.get_services()
        except Exception:
            raise ServiceFetchError()

        try:
            if not services or "value" not in services:
                raise
            return [Service(**service) for service in services["value"]]
        except Exception:
            raise ServiceParseError()

    async def get_hosts(self) -> list[Host]:
        """
        Fetch and deserialize all hosts from the Checkmk API.

        Returns:
            list[Host]: List of hosts, or an empty list on failure.
        """
        hosts = await self.http.get_hosts()

        if not hosts or "value" not in hosts:
            return []

        return [Host(**host) for host in hosts["value"]]
