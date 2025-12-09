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

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from .exceptions import HostNoProblemError, HostProblemAlreadyAcknowledgedError
from .models import Comment, HostAcknowledgement, HostComment, Link, normalize_comments
from .state import ConnectionState

if TYPE_CHECKING:
    from .service import Service


class HostExtensions(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    state: int
    last_check: Optional[int] = None
    acknowledged: Optional[int] = None
    acknowledgement_type: Optional[int] = None
    custom_variables: Optional[dict] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    comments_with_extra_info: Optional[List[Comment]] = None

    @field_validator("comments_with_extra_info", mode="before")
    @classmethod
    def parse_comments(cls, v):
        return normalize_comments(v)


class Host(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    domain_type: str = Field(alias="domainType")
    id: str
    title: str
    members: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    extensions: HostExtensions
    links: List[Link]

    _state: ConnectionState = PrivateAttr()

    @property
    def comments(self):
        return self.extensions.comments_with_extra_info

    @property
    def name(self):
        return self.extensions.name

    @property
    def acknowledged(self) -> bool:
        return bool(self.extensions.acknowledged)

    @property
    def state(self) -> Enum:
        return HostStates(self.extensions.state)

    @property
    def problem(self) -> bool:
        return self.state.value != 0

    async def acknowledge(
        self, comment: str, *, sticky: bool = True, persistent: bool = False, notify: bool = True
    ) -> None:
        """
        Acknowledge this host.

        Args:
            comment: The acknowledgement comment
            sticky: Whether the acknowledgement is sticky
            persistent: Whether the acknowledgement persists across restarts
            notify: Whether to send notifications
        """

        if self.acknowledged:
            raise HostProblemAlreadyAcknowledgedError(host_name=self.extensions.name)

        if not self.problem:
            raise HostNoProblemError(host_name=self.extensions.name)

        data = HostAcknowledgement(
            host_name=self.extensions.name,
            comment=comment,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )

        return await self._state.http.add_host_acknowledgement(data)

    async def add_comment(self, comment: str, persistent: bool = False) -> HostComment:
        """
        Add a comment to this host.

        Args:
            comment: The comment
            persistent: Whether the acknowledgement persists across restarts
        """
        data = HostComment(host_name=self.extensions.name, comment=comment, persistent=persistent)
        await self._state.http.add_host_comment(data)
        return data

    async def remove_acknowledgement(self) -> None:
        """
        Remove the acknowledgement from this host.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("Host acknowledgement removal is not yet implemented")

    async def get_services(self) -> List["Service"]:
        """
        Fetch all services associated with this host.

        Returns:
            List[Service]: List of Service objects for this host
        """
        from .service import Service

        response = await self._state.http.get_services(host_name=self.name)
        services = []

        for service_data in response.get("value", []):
            service = Service(**service_data)
            service._state = self._state
            services.append(service)

        return services
