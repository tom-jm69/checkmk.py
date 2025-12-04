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
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .models import HostAcknowledgement
from .state import ConnectionState


class HostExtensions(BaseModel):
    host_name: str
    state: int
    last_check: Optional[int] = None
    acknowledged: Optional[int] = None
    acknowledgement_type: Optional[int] = None

    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class Host(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    domain_type: str = Field(alias="domainType")
    id: str
    title: str
    members: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    extensions: HostExtensions

    _state: ConnectionState = PrivateAttr()

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

        data = HostAcknowledgement(
            host_name=self.extensions.host_name,
            comment=comment,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )

        await self._state.http.add_host_acknowledgement(data)

    async def remove_acknowledgement(self) -> None:
        """
        Remove the acknowledgement from this host.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("Host acknowledgement removal is not yet implemented")
