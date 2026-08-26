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
from typing import TYPE_CHECKING, ClassVar, cast

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from .enums import HostStates
from .exceptions import (
    HostGroupFetchError,
    HostNoProblemError,
    HostProblemAlreadyAcknowledgedError,
    NotFound,
)
from .models import (
    Acknowledgement,
    CheckInfo,
    Comment,
    CustomHostData,
    DowntimeCommentInfo,
    FlappingInfo,
    Group,
    HostAcknowledgement,
    HostComment,
    Link,
    NotesInfo,
    NotificationInfo,
    PerformanceInfo,
    PluginOutputInfo,
    StateHistory,
    SystemInfo,
)
from .state import ConnectionState

if TYPE_CHECKING:
    from .host_group import HostGroup
    from .service import Service


class HostExtensions(BaseModel):
    """Host extensions with organized nested data models."""

    name: str
    alias: str
    check_info: CheckInfo
    state_history: StateHistory
    flapping_info: FlappingInfo
    notification_info: NotificationInfo
    performance_info: PerformanceInfo
    output_info: PluginOutputInfo
    downtime_comment_info: DowntimeCommentInfo
    custom_data: CustomHostData
    notes_info: NotesInfo
    system_info: SystemInfo
    acknowledgement_info: Acknowledgement
    groups: Group

    @model_validator(mode="before")
    @classmethod
    def organize_flat_data(cls, data: object) -> object:
        """Transform flat API response into nested structure."""
        if isinstance(data, dict) and "check_info" not in data:
            data = cast(dict[str, object], data)
            result: dict[str, object] = {
                "name": data.get("name"),
                "alias": data.get("alias"),
                "check_info": {
                    "check_command": data.get("check_command"),
                    "check_command_expanded": data.get("check_command_expanded"),
                    "check_flapping_recovery_notification": data.get(
                        "check_flapping_recovery_notification"
                    ),
                    "check_freshness": data.get("check_freshness"),
                    "check_interval": data.get("check_interval"),
                    "check_options": data.get("check_options"),
                    "check_period": data.get("check_period"),
                    "check_type": data.get("check_type"),
                    "checks_enabled": data.get("checks_enabled"),
                    "has_been_checked": data.get("has_been_checked"),
                    "is_executing": data.get("is_executing"),
                    "last_check": data.get("last_check"),
                    "max_check_attempts": data.get("max_check_attempts"),
                    "next_check": data.get("next_check"),
                    "retry_interval": data.get("retry_interval"),
                },
                "state_history": {
                    "state": data.get("state"),
                    "last_state": data.get("last_state"),
                    "last_state_change": data.get("last_state_change"),
                    "previous_hard_state": data.get("previous_hard_state"),
                },
                "flapping_info": {
                    "is_flapping": data.get("is_flapping"),
                    "flap_detection_enabled": data.get("flap_detection_enabled"),
                    "flappiness": data.get("flappiness"),
                    "low_flap_threshold": data.get("low_flap_threshold"),
                    "percent_state_change": data.get("percent_state_change"),
                },
                "notification_info": {
                    "first_notification_delay": data.get("first_notification_delay"),
                    "next_notification": data.get("next_notification"),
                    "no_more_notifications": data.get("no_more_notifications"),
                    "notification_interval": data.get("notification_interval"),
                    "notification_period": data.get("notification_period"),
                    "notification_postponement_reason": data.get(
                        "notification_postponement_reason"
                    ),
                    "notifications_enabled": data.get("notifications_enabled"),
                },
                "performance_info": {
                    "execution_time": data.get("execution_time"),
                    "latency": data.get("latency"),
                    "metrics": data.get("metrics"),
                    "perf_data": data.get("perf_data"),
                    "performance_data": data.get("performance_data"),
                    "pnpgraph_present": data.get("pnpgraph_present"),
                    "process_performance_data": data.get("process_performance_data"),
                },
                "output_info": {
                    "plugin_output": data.get("plugin_output"),
                    "long_plugin_output": data.get("long_plugin_output"),
                },
                "downtime_comment_info": {
                    "comments_with_extra_info": data.get("comments_with_extra_info"),
                    "downtimes_with_extra_info": data.get("downtimes_with_extra_info"),
                    "pending_flex_downtime": data.get("pending_flex_downtime"),
                    "scheduled_downtime_depth": data.get("scheduled_downtime_depth"),
                },
                "custom_data": {
                    "custom_variable_names": data.get("custom_variable_names"),
                    "custom_variable_values": data.get("custom_variable_values"),
                    "custom_variables": data.get("custom_variables"),
                    "labels": data.get("labels"),
                    "tags": data.get("tags"),
                },
                "notes_info": {
                    "notes": data.get("notes"),
                    "notes_expanded": data.get("notes_expanded"),
                    "notes_url": data.get("notes_url"),
                    "notes_url_expanded": data.get("notes_url_expanded"),
                },
                "system_info": {
                    "modified_attributes": data.get("modified_attributes"),
                    "modified_attributes_list": data.get("modified_attributes_list"),
                },
                "acknowledgement_info": {
                    "acknowledgement_type": data.get("acknowledgement_type"),
                    "acknowledged": data.get("acknowledged"),
                },
                "groups": {
                    "groups": data.get("groups"),
                },
            }
            return result
        return data  # pyright: ignore[reportUnknownVariableType]


class Host(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    domain_type: str = Field(alias="domainType")
    id: str
    title: str
    members: dict[str, object] | None = None
    updated_at: datetime | None = Field(default_factory=datetime.now)
    extensions: HostExtensions
    links: list[Link]

    _state: ConnectionState = PrivateAttr()

    def bind_state(self, state: ConnectionState) -> None:
        """Attach the shared connection state. Called by `Client`/`Host` after construction."""
        self._state = state

    @property
    def _ext(self) -> HostExtensions:
        return self.extensions

    @property
    def comments(self) -> list[Comment] | None:
        return self._ext.downtime_comment_info.comments_with_extra_info

    @property
    def acknowledged(self) -> bool:
        return bool(self._ext.acknowledgement_info.acknowledged)

    @property
    def host_name(self) -> str:
        return self._ext.name

    @property
    def name(self) -> str:
        return self._ext.name

    @property
    def alias(self) -> str:
        return self._ext.alias

    @property
    def state(self) -> HostStates:
        return HostStates(self._ext.state_history.state)

    @property
    def problem(self) -> bool:
        return self.state.value != 0

    @property
    def custom_variables(self) -> dict[str, str] | None:
        return self._ext.custom_data.custom_variables

    @property
    def tags(self) -> dict[str, str] | None:
        return self._ext.custom_data.tags

    @property
    def ipv4(self) -> str | None:
        custom_variables = self.custom_variables
        if custom_variables:
            return custom_variables.get("ADDRESS_4")
        return None

    @property
    def ipv6(self) -> str | None:
        custom_variables = self.custom_variables
        if custom_variables:
            return custom_variables.get("ADDRESS_6")
        return None

    @property
    def groups(self) -> list[str] | None:
        """The groups property."""
        return self._ext.groups.groups if self._ext.groups else None

    async def acknowledge(
        self, comment: str, *, sticky: bool = True, persistent: bool = False, notify: bool = True
    ) -> bool:
        """
        Acknowledge this host.

        Args:
            comment: The acknowledgement comment
            sticky: Whether the acknowledgement is sticky
            persistent: Whether the acknowledgement persists across restarts
            notify: Whether to send notifications
        """

        if self.acknowledged:
            raise HostProblemAlreadyAcknowledgedError(host_name=self.host_name)

        if not self.problem:
            raise HostNoProblemError(host_name=self.host_name)

        data = HostAcknowledgement(
            host_name=self.host_name,
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
        data = HostComment(host_name=self.host_name, comment=comment, persistent=persistent)
        _ = await self._state.http.add_host_comment(data)
        return data

    async def remove_acknowledgement(self) -> None:
        """
        Remove the acknowledgement from this host.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("Host acknowledgement removal is not yet implemented")

    async def get_services(self) -> list["Service"]:
        """
        Fetch all services associated with this host.

        Returns:
            List[Service]: List of Service objects for this host
        """
        from .http import value_list
        from .service import Service

        response = await self._state.http.get_services(host_name=self.name)
        services: list[Service] = []

        for service_data in value_list(response):
            service = Service.model_validate(service_data)
            service.bind_state(self._state)
            services.append(service)

        return services

    async def get_groups(self) -> list["HostGroup"]:
        """
        Fetch all host groups this host is a member of.

        Built-in pseudo-groups (e.g. `check_mk`) that have no corresponding
        `host_group_config` object are silently skipped.

        Returns:
            List[HostGroup]: List of HostGroup objects for this host's groups.
        """
        from .host_group import HostGroup

        groups: list[HostGroup] = []

        for group_name in self.groups or []:
            try:
                group_data = await self._state.http.get_host_group(group_name)
            except HostGroupFetchError as e:
                if isinstance(e.__cause__, NotFound):
                    continue
                raise
            group = HostGroup.model_validate(group_data)
            group.bind_state(self._state)
            groups.append(group)

        return groups
