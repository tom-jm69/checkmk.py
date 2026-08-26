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
from typing import cast

import aiohttp
from pydantic import BaseModel

from ._version import __version__
from .constants import (
    CHECKMK_ACKNOWLEDGE_HOST_ENDPOINT,
    CHECKMK_ACKNOWLEDGE_SERVICE_ENDPOINT,
    CHECKMK_ADD_HOST_COMMENT_ENDPOINT,
    CHECKMK_ADD_SERVICE_COMMENT_ENDPOINT,
    CHECKMK_HOST_GROUP_ENDPOINT,
    CHECKMK_HOST_GROUPS_ENDPOINT,
    CHECKMK_HOSTS_ENDPOINT,
    CHECKMK_SERVICE_ENDPOINT,
    CHECKMK_SERVICE_GROUP_ENDPOINT,
    CHECKMK_SERVICE_GROUPS_ENDPOINT,
    CHECKMK_SERVICES_ENDPOINT,
)
from .exceptions import (
    Forbidden,
    HostFetchError,
    HostGroupFetchError,
    HostGroupParseError,
    HostParseError,
    HTTPError,
    NotFound,
    ServiceFetchError,
    ServiceGroupFetchError,
    ServiceGroupParseError,
    ServiceParseError,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
)
from .models import (
    APIAuth,
    CheckmkHostColumns,
    CheckmkServiceColumns,
    ColumnsRequest,
    HostAcknowledgement,
    HostComment,
    ServiceAcknowledgementRequest,
    ServiceComment,
)

_log = logging.getLogger(__name__)

JSONDict = dict[str, object]
Params = dict[str, str | int | bool | list[str]]


def value_list(response: JSONDict) -> list[JSONDict]:
    """Extract the `"value"` list of JSON objects from a Checkmk collection response."""
    value = response.get("value")
    if not isinstance(value, list):
        return []
    return [item for item in cast(list[object], value) if isinstance(item, dict)]


class Route(BaseModel):
    base_url: str
    method: str
    path: str

    @property
    def url(self) -> str:
        return self.base_url + self.path


async def json_or_text(resp: aiohttp.ClientResponse) -> JSONDict | str:
    ctype = resp.headers.get("Content-Type", "")
    # Try json first if plausible, fall back to text
    if "application/json" in ctype or "json" in ctype:
        try:
            return cast(JSONDict, await resp.json(content_type=None))
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
        self.timeout: int = timeout
        self.retries: int = retries
        self.verify_ssl: bool = verify_ssl
        self.__session: aiohttp.ClientSession | None
        try:
            _ = asyncio.get_running_loop()
            self.__session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(self.timeout),
                connector=aiohttp.TCPConnector(ssl=self.verify_ssl),
            )
        except RuntimeError:
            self.__session = None
        self.auth: APIAuth | None = None
        self.api_key: str | None = None
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

    async def start_session(self) -> None:
        self.__session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(self.timeout),
            connector=aiohttp.TCPConnector(ssl=self.verify_ssl),
        )

    async def request(
        self,
        route: Route,
        params: Params | None = None,
        json_body: JSONDict | None = None,
        data: str | None = None,
        max_retries: int = 3,
    ) -> JSONDict | str:
        method = route.method
        url = route.url

        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
        }

        if self.auth is not None:
            headers["Authorization"] = self.auth.to_header()

        if self.__session is None:
            await self.start_session()
        session = self.__session
        assert session is not None

        # Retry loop with exponential backoff
        async with self.ratelimit_lock:
            for attempt in range(max_retries):
                try:
                    async with session.request(
                        method,
                        url,
                        headers=headers,
                        params=params,
                        json=json_body,
                        data=data,
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
                                retry_after = int(response.headers.get("Retry-After", "60"))
                                attempt_info = f"attempt {attempt + 1}/{max_retries}"
                                _log.warning(
                                    f"{method} {url} rate-limited. Retrying after {retry_after}s ({attempt_info})"
                                )
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                raise TooManyRequests(response, response_data)

                        if response.status == 401:
                            raise Unauthorized(response, response_data)

                        if response.status == 403:
                            raise Forbidden(response, response_data)

                        if response.status == 404:
                            raise NotFound(response, response_data)

                        if response.status in {500, 502, 504, 503, 524}:
                            if attempt < max_retries - 1:
                                backoff = cast(int, 2**attempt)  # 1s, 2s, 4s
                                attempt_info = f"attempt {attempt + 1}/{max_retries}"
                                _log.warning(
                                    f"{method} {url} server error {response.status}. Retrying in {backoff}s ({attempt_info})"
                                )
                                await asyncio.sleep(backoff)
                                continue
                            else:
                                raise ServiceUnavailable(response, response_data)

                except aiohttp.ClientError as e:
                    if attempt < max_retries - 1:
                        client_backoff = cast(int, 2**attempt)
                        attempt_info = f"attempt {attempt + 1}/{max_retries}"
                        _log.warning(
                            f"{method} {url} client error: {e}. Retrying in {client_backoff}s ({attempt_info})"
                        )
                        await asyncio.sleep(client_backoff)
                        continue
                    raise
            raise RuntimeError("Unreachable code in HTTP handling")

    async def request_json(
        self,
        route: Route,
        params: Params | None = None,
        json_body: JSONDict | None = None,
        data: str | None = None,
        max_retries: int = 3,
    ) -> JSONDict:
        result = await self.request(
            route, params=params, json_body=json_body, data=data, max_retries=max_retries
        )
        if not isinstance(result, dict):
            raise HTTPError(
                message=f"Expected a JSON object response from {route.method} {route.url}",
                response_data=result,
                url=route.url,
            )
        return result


class CheckmkHTTP:
    def __init__(
        self,
        url: str,
        username: str,
        secret: str,
        verify_ssl: bool,
        timeout: int,
        retries: int,
    ) -> None:
        self.url: str = url
        self.verify_ssl: bool = verify_ssl
        self.timeout: int = timeout
        self.client: HTTPClient = HTTPClient(timeout=self.timeout, verify_ssl=self.verify_ssl)
        self.retries: int = retries
        self.username: str = username
        self.secret: str = secret
        self.set_auth()

    async def close(self) -> None:
        await self.client.close()

    def set_api_key(self, api_key: str) -> None:
        self.client.set_api_key(api_key)

    async def get_service(self, host_name: str, service_description: str) -> JSONDict:
        columns_request_data = CheckmkServiceColumns.get_columns()

        params: Params = {
            "service_description": service_description,
            "columns": columns_request_data,
        }

        return await self.client.request_json(
            Route(
                base_url=self.url,
                method="GET",
                path=CHECKMK_SERVICE_ENDPOINT.format(host_name=host_name),
            ),
            params=params,
        )

    async def get_services(self, host_name: str | None = None) -> JSONDict:
        columns_request_data = CheckmkServiceColumns.get_columns()

        data = ColumnsRequest(columns=columns_request_data).model_dump_json()

        params: Params = {}
        if host_name:
            params["host_name"] = host_name

        try:
            response = await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="POST",
                    path=CHECKMK_SERVICES_ENDPOINT,
                ),
                params=params if params else None,
                data=data,
            )
        except Exception as e:
            raise ServiceFetchError(
                message=f"API request failed: {e}",
            ) from e

        if "value" not in response:
            raise ServiceParseError(
                message="Invalid response structure: missing 'value' field", raw_data=response
            )

        return response

    def set_auth(self) -> None:
        self.client.auth = APIAuth(username=self.username, secret=self.secret)

    async def get_hosts(self) -> JSONDict:
        columns_request_data = CheckmkHostColumns.get_columns(["name", "alias"])
        data = ColumnsRequest(columns=columns_request_data).model_dump_json()

        try:
            response = await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="POST",
                    path=CHECKMK_HOSTS_ENDPOINT,
                ),
                data=data,
            )
        except Exception as e:
            raise HostFetchError(
                message=f"API request failed: {e}",
            ) from e

        if "value" not in response:
            raise HostParseError(
                message="Invalid response structure: missing 'value' field", raw_data=response
            )
        return response

    async def get_host_groups(self) -> JSONDict:
        try:
            response = await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="GET",
                    path=CHECKMK_HOST_GROUPS_ENDPOINT,
                ),
            )
        except Exception as e:
            raise HostGroupFetchError(
                message=f"API request failed: {e}",
            ) from e

        if "value" not in response:
            raise HostGroupParseError(
                message="Invalid response structure: missing 'value' field", raw_data=response
            )
        return response

    async def get_host_group(self, name: str) -> JSONDict:
        try:
            return await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="GET",
                    path=CHECKMK_HOST_GROUP_ENDPOINT.format(name=name),
                ),
            )
        except Exception as e:
            raise HostGroupFetchError(
                message=f"API request failed: {e}",
                host_group_name=name,
            ) from e

    async def get_service_groups(self) -> JSONDict:
        try:
            response = await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="GET",
                    path=CHECKMK_SERVICE_GROUPS_ENDPOINT,
                ),
            )
        except Exception as e:
            raise ServiceGroupFetchError(
                message=f"API request failed: {e}",
            ) from e

        if "value" not in response:
            raise ServiceGroupParseError(
                message="Invalid response structure: missing 'value' field", raw_data=response
            )
        return response

    async def get_service_group(self, name: str) -> JSONDict:
        try:
            return await self.client.request_json(
                Route(
                    base_url=self.url,
                    method="GET",
                    path=CHECKMK_SERVICE_GROUP_ENDPOINT.format(name=name),
                ),
            )
        except Exception as e:
            raise ServiceGroupFetchError(
                message=f"API request failed: {e}",
                service_group_name=name,
            ) from e

    async def add_service_comment(self, comment: ServiceComment) -> bool:
        data = comment.model_dump_json()

        _ = await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ADD_SERVICE_COMMENT_ENDPOINT,
            ),
            data=data,
        )
        return True

    async def add_host_comment(self, comment: HostComment) -> bool:
        data = comment.model_dump_json()

        _ = await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ADD_HOST_COMMENT_ENDPOINT,
            ),
            data=data,
        )
        return True

    async def add_host_acknowledgement(self, acknowledgement: HostAcknowledgement) -> bool:
        data = acknowledgement.model_dump_json()

        _ = await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ACKNOWLEDGE_HOST_ENDPOINT,
            ),
            data=data,
        )
        return True

    async def add_service_acknowledgement(
        self, acknowledgement: ServiceAcknowledgementRequest
    ) -> bool:
        data = acknowledgement.model_dump_json()

        _ = await self.client.request(
            Route(
                base_url=self.url,
                method="POST",
                path=CHECKMK_ACKNOWLEDGE_SERVICE_ENDPOINT,
            ),
            data=data,
        )
        return True
