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

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Iterable, List, Optional

import aiohttp
from pydantic import BaseModel

from . import __version__
from .constants import (CHECKMK_ACKNOWLEDGE_HOST_ENDPOINT,
                        CHECKMK_ACKNOWLEDGE_SERVICE_ENDPOINT,
                        CHECKMK_ADD_HOST_COMMENT_ENDPOINT,
                        CHECKMK_ADD_SERVICE_COMMENT_ENDPOINT,
                        CHECKMK_HOSTS_ENDPOINT, CHECKMK_SERVICES_ENDPOINT)
from .exceptions import (Forbidden, HTTPError, NotFound, ServiceUnavailable,
                         TooManyRequests, Unauthorized)
from .models import (APIAuth, ColumnsRequest, HostAcknowledgement, HostComment,
                     ServiceAcknowledgement, ServiceComment)

_log = logging.getLogger(__name__)

class Route(BaseModel):
    base_url: str
    method: str
    path: str

    @property
    def url(self):
        return self.base_url + self.path


async def json_or_text(resp: aiohttp.ClientResponse) -> dict | str:
    ctype = resp.headers.get("Content-Type", "")
    # Try json first if plausible, fall back to text
    if "application/json" in ctype or "json" in ctype:
        try:
            return await resp.json(content_type=None)
        except (json.JSONDecodeError, aiohttp.ContentTypeError):
            pass
    return await resp.text()


class HTTPClient:
    def __init__(
        self,
        verify_ssl: bool = False,
        timeout: int = 30,
        retries: int = 5,
    ) -> None:
        # Checks if the faceit.Client was initialized before or after the event loop started
        # If it was not initialized, you have to call start_session()
        self.timeout = timeout
        self.retries = retries
        self.verify_ssl = verify_ssl
        try:
            asyncio.get_running_loop()
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(self.timeout),
                connector=aiohttp.TCPConnector(ssl=self.verify_ssl),
            )
        except RuntimeError:
            self.__session = None
        self.auth = None
        self.ratelimit_lock: asyncio.Lock = asyncio.Lock()
        user_agent = "checkmk.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(
            __version__, sys.version_info, str(aiohttp.__version__)
        )

    def set_api_key(self, api_key: str) -> None:
        self.api_key = f"Bearer {api_key}"

    async def close(self) -> None:
        if self.__session:
            await self.__session.close()

    async def start_session(self):
        self.__session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(self.timeout),
            connector=aiohttp.TCPConnector(verify_ssl=self.verify_ssl),
        )

    async def request(
        self,
        route: Route,
        params: Optional[Iterable[Dict[str, Any]]] = None,
        json_body: Optional[dict] = None,
        data: Optional[Any] = None,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> dict[str, Any] | str:
        method = route.method
        url = route.url

        headers: Dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }

        if self.auth is not None:
            headers["Authorization"] = self.auth.to_header()

        kwargs["headers"] = {**headers, **kwargs.get("headers", {})}

        if params:
            kwargs["params"] = params

        if json_body:
            kwargs["json"] = json_body

        if data:
            kwargs["data"] = data

        # Retry loop with exponential backoff
        async with self.ratelimit_lock:
            for attempt in range(max_retries):
                try:
                    async with self.__session.request(
                        method, url, **kwargs
                    ) as response:
                        _log.debug(
                            f"{method} {url} with {params} returned status {response.status}"
                        )

                        response_data = await json_or_text(response)

                        if 200 <= response.status < 300:
                            _log.debug(f"{method} {url} received: {response_data}")
                            return response_data

                        if response.status == 429:
                            if attempt < max_retries - 1:
                                retry_after = int(
                                    response.headers.get("Retry-After", "60")
                                )
                                _log.warning(
                                    f"{method} {url} rate-limited. "
                                    f"Retrying after {retry_after}s (attempt {attempt + 1}/{max_retries})"
                                )
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                raise TooManyRequests(response, response_data)

                        if response.status in {500, 502, 503, 504}:
                            if attempt < max_retries - 1:
                                backoff = 2**attempt  # 1s, 2s, 4s
                                _log.warning(
                                    f"{method} {url} server error {response.status}. "
                                    f"Retrying in {backoff}s (attempt {attempt + 1}/{max_retries})"
                                )
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                raise ServiceUnavailable(response, response_data)

                        if response.status == 401:
                            raise Unauthorized(response, response_data)
                        if response.status == 403:
                            raise Forbidden(response, response_data)
                        if response.status == 404:
                            raise NotFound(response, response_data)
                        raise HTTPError(response, response_data)

                except aiohttp.ClientError as e:
                    if attempt < max_retries - 1:
                        backoff = 2**attempt
                        _log.warning(
                            f"{method} {url} client error: {e}. "
                            f"Retrying in {backoff}s (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    raise

            raise HTTPError(None, "Max retries exceeded")



class CheckmkHTTP:
    def __init__(
        self,
        url: str,
        username: str,
        secret: str,
        verify_ssl: bool,
        timeout: int,
        retries: int,
    ):
        self.url = url
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.client = HTTPClient(timeout=self.timeout, verify_ssl=self.verify_ssl)
        self.retries = retries
        self.username = username
        self.secret = secret
        self.set_auth()

    async def close(self) -> None:
        await self.client.close()

    async def get_services(self, **parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        columns_request_data = [
            "host_name",
            "description",
            "state",
            "last_check",
            "acknowledged",
            "acknowledgement_type",
            "check_command",
            "check_command_expanded",
            "check_flapping_recovery_notification",
            "check_freshness",
            "check_interval",
            "check_options",
            "check_period",
            "check_type",
            "checks_enabled",
            "execution_time",
            "flap_detection_enabled",
            "flappiness",
            "has_been_checked",
            "last_state",
            "last_state_change",
            "last_notification",
            "next_check",
            "next_notification",
            "notifications_enabled",
            "plugin_output",
            "long_plugin_output",
            "comments_with_extra_info",
        ]

        data = ColumnsRequest(columns=columns_request_data).model_dump_json()
        response = await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_SERVICES_ENDPOINT,
            ),
            data=data,
        )
        return response

    def set_auth(self) -> None:
        self.client.auth = APIAuth(username=self.username, secret=self.secret)

    async def get_hosts(self, **parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        columns_request_data = [
            "name",
            "state",
            "last_check",
            "acknowledged",
            "acknowledgement_type",
        ]

        data = ColumnsRequest(columns=columns_request_data).model_dump_json()

        return await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_HOSTS_ENDPOINT,
            ),
            data=data,
        )

    async def add_service_comment(self, comment: ServiceComment) -> Dict[str, Any]:
        data = comment.model_dump_json()

        return await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ADD_SERVICE_COMMENT_ENDPOINT,
            ),
            data=data,
        )

    async def add_host_comment(self, comment: HostComment) -> Dict[str, Any]:
        data = comment.model_dump_json()

        return await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ADD_HOST_COMMENT_ENDPOINT,
            ),
            data=data,
        )

    async def add_host_acknowledgement(
        self, acknowledgement: HostAcknowledgement
    ) -> Dict[str, Any]:
        data = acknowledgement.model_dump_json()

        return await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ACKNOWLEDGE_HOST_ENDPOINT,
            ),
            data=data,
        )

    async def add_service_acknowledgement(
        self, acknowledgement: ServiceAcknowledgement
    ) -> Dict[str, Any]:
        data = acknowledgement.model_dump_json()

        return await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ACKNOWLEDGE_SERVICE_ENDPOINT,
            ),
            data=data,
        )

