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

import aiohttp
from typing_extensions import override

ResponseData = dict[str, object] | str


class CheckmkException(Exception):
    """Base exception class for all checkmk library errors"""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message)
        self.message: str = message
        self.details: dict[str, object] = kwargs

    @override
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
        status_code: int | None = None,
        response_data: ResponseData | None = None,
        url: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, url=url)
        self.status_code: int | None = status_code
        self.response_data: ResponseData | None = response_data
        self.url: str | None = url

    @override
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
        raw_data: ResponseData | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.raw_data: ResponseData | None = raw_data
        self.field: str | None = field


class FetchError(CheckmkException):
    """Base exception class for fetch errors"""

    def __init__(
        self,
        message: str,
        resource_id: str | None = None,
        resource_type: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type=resource_type)
        self.resource_id: str | None = resource_id
        self.resource_type: str | None = resource_type


class ProblemAcknowledgementError(CheckmkException):
    """Base exception for all acknowledgement-related errors"""

    pass


class HostException(CheckmkException):
    """Base exception for all host-related errors"""

    pass


class ServiceException(CheckmkException):
    """Base exception for all service-related errors"""

    pass


class HostGroupException(CheckmkException):
    """Base exception for all host group-related errors"""

    pass


class ServiceGroupException(CheckmkException):
    """Base exception for all service group-related errors"""

    pass


class ServiceParseError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ServiceException, ParseError
):
    """Raised when a raw checkmk service object can't be properly parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: ResponseData | None = None,
        field: str | None = None,
        service_description: str | None = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.service_description: str | None = service_description
        if service_description:
            self.details["service_description"] = service_description


class ServiceFetchError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ServiceException, FetchError
):
    """Raised when a checkmk service could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: str | None = None,
        service_description: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="service")
        self.service_description: str | None = service_description
        if service_description:
            self.details["service_description"] = service_description


class ServiceNoProblemError(ServiceException, ProblemAcknowledgementError):
    def __init__(
        self,
        message: str = "Service Problem Acknowledgement failed",
        resource_id: str | None = None,
        service_description: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="service")
        self.service_description: str | None = service_description
        if service_description:
            self.details["service_description"] = service_description


class ServiceProblemAlreadyAcknowledgedError(ServiceException, ProblemAcknowledgementError):
    def __init__(
        self,
        message: str = "Service Problem already acknowledged",
        resource_id: str | None = None,
        service_description: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="service")
        self.service_description: str | None = service_description
        if service_description:
            self.details["service_description"] = service_description


class HostNoProblemError(HostException, ProblemAcknowledgementError):
    def __init__(
        self,
        message: str = "Host Problem Acknowledgement failed",
        resource_id: str | None = None,
        host_name: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="host")
        self.host_name: str | None = host_name
        if host_name:
            self.details["host_name"] = host_name


class HostProblemAlreadyAcknowledgedError(HostException, ProblemAcknowledgementError):
    def __init__(
        self,
        message: str = "Host Problem already acknowledged",
        resource_id: str | None = None,
        host_name: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="host")
        self.host_name: str | None = host_name
        if host_name:
            self.details["host_name"] = host_name


class HostGroupFetchError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    HostGroupException, FetchError
):
    """Raised when a checkmk host group could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: str | None = None,
        host_group_name: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="host_group")
        self.host_group_name: str | None = host_group_name
        if host_group_name:
            self.details["host_group_name"] = host_group_name


class HostGroupParseError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    HostGroupException, ParseError
):
    """Raised when a checkmk host group object could not be parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: ResponseData | None = None,
        field: str | None = None,
        host_group_name: str | None = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.host_group_name: str | None = host_group_name
        if host_group_name:
            self.details["host_group_name"] = host_group_name


class ServiceGroupFetchError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ServiceGroupException, FetchError
):
    """Raised when a checkmk service group could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: str | None = None,
        service_group_name: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="service_group")
        self.service_group_name: str | None = service_group_name
        if service_group_name:
            self.details["service_group_name"] = service_group_name


class ServiceGroupParseError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    ServiceGroupException, ParseError
):
    """Raised when a checkmk service group object could not be parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: ResponseData | None = None,
        field: str | None = None,
        service_group_name: str | None = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.service_group_name: str | None = service_group_name
        if service_group_name:
            self.details["service_group_name"] = service_group_name


class HostFetchError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    HostException, FetchError
):
    """Raised when a checkmk host could not be fetched"""

    def __init__(
        self,
        message: str = "API request failed",
        resource_id: str | None = None,
        host_name: str | None = None,
    ) -> None:
        super().__init__(message, resource_id=resource_id, resource_type="host")
        self.host_name: str | None = host_name
        if host_name:
            self.details["host_name"] = host_name


class HostParseError(  # pyright: ignore[reportUnsafeMultipleInheritance]
    HostException, ParseError
):
    """Raised when a checkmk host object could not be parsed"""

    def __init__(
        self,
        message: str = "Parsing failed",
        raw_data: ResponseData | None = None,
        field: str | None = None,
        host_name: str | None = None,
    ) -> None:
        super().__init__(message, raw_data=raw_data, field=field)
        self.host_name: str | None = host_name
        if host_name:
            self.details["host_name"] = host_name


# HTTP-specific error classes for aiohttp integration
class Unauthorized(HTTPError):
    """Raised when authentication fails (401)"""

    def __init__(
        self,
        response: aiohttp.ClientResponse | None,
        data: ResponseData,
    ) -> None:
        status = response.status if response else 401
        url = str(response.url) if response else None
        super().__init__(
            message=f"Unauthorized: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response: aiohttp.ClientResponse | None = response


class Forbidden(HTTPError):
    """Raised when access is forbidden (403)"""

    def __init__(
        self,
        response: aiohttp.ClientResponse | None,
        data: ResponseData,
    ) -> None:
        status = response.status if response else 403
        url = str(response.url) if response else None
        super().__init__(
            message=f"Forbidden: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response: aiohttp.ClientResponse | None = response


class NotFound(HTTPError):
    """Raised when resource is not found (404)"""

    def __init__(
        self,
        response: aiohttp.ClientResponse | None,
        data: ResponseData,
    ) -> None:
        status = response.status if response else 404
        url = str(response.url) if response else None
        super().__init__(
            message=f"Not Found: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response: aiohttp.ClientResponse | None = response


class TooManyRequests(HTTPError):
    """Raised when rate limit is exceeded (429)"""

    def __init__(
        self,
        response: aiohttp.ClientResponse | None,
        data: ResponseData,
    ) -> None:
        status = response.status if response else 429
        url = str(response.url) if response else None
        super().__init__(
            message=f"Too Many Requests: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response: aiohttp.ClientResponse | None = response


class ServiceUnavailable(HTTPError):
    """Raised when service is unavailable (5xx)"""

    def __init__(
        self,
        response: aiohttp.ClientResponse | None,
        data: ResponseData,
    ) -> None:
        status = response.status if response else 503
        url = str(response.url) if response else None
        super().__init__(
            message=f"Service Unavailable: {data}",
            status_code=status,
            response_data=data,
            url=url,
        )
        self.response: aiohttp.ClientResponse | None = response
