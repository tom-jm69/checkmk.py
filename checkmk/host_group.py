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
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .enums import HostStates, ServiceStates
from .models import HostGroupExtensions, HostMemberState, Link
from .state import ConnectionState


class HostGroup(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    domain_type: str = Field(alias="domainType")
    id: str
    title: str
    members: Optional[Dict[str, Any]] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    extensions: HostGroupExtensions
    links: List[Link]

    _state: ConnectionState = PrivateAttr()

    @property
    def _ext(self) -> HostGroupExtensions:
        return self.extensions

    @property
    def name(self) -> str:
        return self._ext.name

    @property
    def alias(self) -> str:
        return self._ext.alias

    @property
    def action_url(self) -> str | None:
        return self._ext.action_url

    @property
    def notes(self) -> str | None:
        return self._ext.notes

    @property
    def notes_url(self) -> str | None:
        return self._ext.notes_url

    @property
    def hosts(self) -> list[str] | None:
        return self._ext.members

    @property
    def hosts_with_state(self) -> List[HostMemberState] | None:
        return self._ext.members_with_state

    @property
    def num_hosts(self) -> int | None:
        return self._ext.num_hosts

    @property
    def num_hosts_up(self) -> int | None:
        return self._ext.num_hosts_up

    @property
    def num_hosts_down(self) -> int | None:
        return self._ext.num_hosts_down

    @property
    def num_hosts_unreach(self) -> int | None:
        return self._ext.num_hosts_unreach

    @property
    def num_hosts_pending(self) -> int | None:
        return self._ext.num_hosts_pending

    @property
    def num_hosts_handled_problems(self) -> int | None:
        return self._ext.num_hosts_handled_problems

    @property
    def num_hosts_unhandled_problems(self) -> int | None:
        return self._ext.num_hosts_unhandled_problems

    @property
    def num_services(self) -> int | None:
        return self._ext.num_services

    @property
    def num_services_ok(self) -> int | None:
        return self._ext.num_services_ok

    @property
    def num_services_warn(self) -> int | None:
        return self._ext.num_services_warn

    @property
    def num_services_crit(self) -> int | None:
        return self._ext.num_services_crit

    @property
    def num_services_unknown(self) -> int | None:
        return self._ext.num_services_unknown

    @property
    def num_services_pending(self) -> int | None:
        return self._ext.num_services_pending

    @property
    def num_services_handled_problems(self) -> int | None:
        return self._ext.num_services_handled_problems

    @property
    def num_services_unhandled_problems(self) -> int | None:
        return self._ext.num_services_unhandled_problems

    @property
    def num_services_hard_ok(self) -> int | None:
        return self._ext.num_services_hard_ok

    @property
    def num_services_hard_warn(self) -> int | None:
        return self._ext.num_services_hard_warn

    @property
    def num_services_hard_crit(self) -> int | None:
        return self._ext.num_services_hard_crit

    @property
    def num_services_hard_unknown(self) -> int | None:
        return self._ext.num_services_hard_unknown

    @property
    def worst_host_state(self) -> Enum | None:
        if self._ext.worst_host_state is None:
            return None
        return HostStates(self._ext.worst_host_state)

    @property
    def worst_service_state(self) -> Enum | None:
        if self._ext.worst_service_state is None:
            return None
        return ServiceStates(self._ext.worst_service_state)

    @property
    def worst_service_hard_state(self) -> Enum | None:
        if self._ext.worst_service_hard_state is None:
            return None
        return ServiceStates(self._ext.worst_service_hard_state)
