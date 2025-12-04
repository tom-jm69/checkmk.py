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

from typing import Any, Optional

import aiohttp


class CheckmkException(Exception):
    """Base exception class for all checkmk library errors"""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message)
        self.message = message
        self.details = kwargs

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class HTTPError(CheckmkException):
    """Raised when an HTTP request to the Checkmk API fails"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
        url: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code=status_code, url=url)
        self.status_code = status_code
        self.response_data = response_data
        self.url = url

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.url:
            parts.append(f"URL: {self.url}")
        if self.response_data:
            parts.append(f"Response: {self.response_data}")
        return " | ".join(parts)


class ParseError(CheckmkException):
    """Base exception class for parse errors"""

    def __init__(
        self,
        message: str,
        raw_data: Optional[Any] = None,
        field: Optional[str] = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.raw_data = raw_data
        self.field = field


class FetchError(CheckmkException):
    """Base exception class for fetch errors"""

    def __init__(
        self,
        message: str,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type=resource_type)
        self.resource_id = resource_id
        self.resource_type = resource_type


class ServiceParseError(ParseError):
    """Raised when a raw checkmk service object can't be properly parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: Optional[Any] = None,
        field: Optional[str] = None,
        service_description: Optional[str] = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.service_description = service_description
        if service_description:
            self.details["service_description"] = service_description


class ServiceFetchError(FetchError):
    """Raised when a checkmk service could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: Optional[str] = None,
        service_description: Optional[str] = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="service")
        self.service_description = service_description
        if service_description:
            self.details["service_description"] = service_description


class HostFetchError(FetchError):
    """Raised when a checkmk host could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: Optional[str] = None,
        host_name: Optional[str] = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="host")
        self.host_name = host_name
        if host_name:
            self.details["host_name"] = host_name


class HostParseError(ParseError):
    """Raised when a checkmk host object could not be parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: Optional[Any] = None,
        field: Optional[str] = None,
        host_name: Optional[str] = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.host_name = host_name
        if host_name:
            self.details["host_name"] = host_name


# HTTP-specific error classes for aiohttp integration
class Unauthorized(HTTPError):
    """Raised when authentication fails (401)"""

    def __init__(
        self,
        response: Optional[aiohttp.ClientResponse],
        data: Any,
    ) -> None:
        status = response.status if response else 401
        url = str(response.url) if response else None
        super().__init__(
            message=f"Unauthorized: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response = response


class Forbidden(HTTPError):
    """Raised when access is forbidden (403)"""

    def __init__(
        self,
        response: Optional[aiohttp.ClientResponse],
        data: Any,
    ) -> None:
        status = response.status if response else 403
        url = str(response.url) if response else None
        super().__init__(
            message=f"Forbidden: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response = response


class NotFound(HTTPError):
    """Raised when resource is not found (404)"""

    def __init__(
        self,
        response: Optional[aiohttp.ClientResponse],
        data: Any,
    ) -> None:
        status = response.status if response else 404
        url = str(response.url) if response else None
        super().__init__(
            message=f"Not Found: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response = response


class TooManyRequests(HTTPError):
    """Raised when rate limit is exceeded (429)"""

    def __init__(
        self,
        response: Optional[aiohttp.ClientResponse],
        data: Any,
    ) -> None:
        status = response.status if response else 429
        url = str(response.url) if response else None
        super().__init__(
            message=f"Too Many Requests: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response = response


class ServiceUnavailable(HTTPError):
    """Raised when service is unavailable (5xx)"""

    def __init__(
        self,
        response: Optional[aiohttp.ClientResponse],
        data: Any,
    ) -> None:
        status = response.status if response else 503
        url = str(response.url) if response else None
        super().__init__(
            message=f"Service Unavailable: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response = response
