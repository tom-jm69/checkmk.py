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

from ._version import __version__
from .client import Client
from .exceptions import (
    CheckmkException,
    FetchError,
    Forbidden,
    HostException,
    HostFetchError,
    HostGroupException,
    HostGroupFetchError,
    HostGroupParseError,
    HostNoProblemError,
    HostParseError,
    HostProblemAlreadyAcknowledgedError,
    HTTPError,
    NotFound,
    ParseError,
    ServiceException,
    ServiceFetchError,
    ServiceGroupException,
    ServiceGroupFetchError,
    ServiceGroupParseError,
    ServiceNoProblemError,
    ServiceParseError,
    ServiceProblemAlreadyAcknowledgedError,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
)
from .host import Host
from .host_group import HostGroup
from .service import Service
from .service_group import ServiceGroup

__all__ = [
    "Client",
    "CheckmkException",
    "FetchError",
    "Forbidden",
    "HostException",
    "HostFetchError",
    "HostParseError",
    "HostGroupException",
    "HostGroupFetchError",
    "HostGroupParseError",
    "HTTPError",
    "NotFound",
    "ParseError",
    "ServiceException",
    "ServiceFetchError",
    "ServiceNoProblemError",
    "ServiceParseError",
    "ServiceGroupException",
    "ServiceGroupFetchError",
    "ServiceGroupParseError",
    "ServiceUnavailable",
    "TooManyRequests",
    "Unauthorized",
    "HostNoProblemError",
    "HostProblemAlreadyAcknowledgedError",
    "ServiceProblemAlreadyAcknowledgedError",
    "Service",
    "Host",
    "HostGroup",
    "ServiceGroup",
]
logging.getLogger(__name__).addHandler(logging.NullHandler())
