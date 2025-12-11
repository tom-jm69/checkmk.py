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

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from .enums import HostStates
from .exceptions import HostNoProblemError, HostProblemAlreadyAcknowledgedError
from .models import (
    Acknowledgement,
    CheckInfo,
    Comment,
    CustomHostData,
    DowntimeCommentInfo,
    FlappingInfo,
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
    from .service import Service


class HostExtensions(BaseModel):
    """Host extensions with organized nested data models."""

    # Grouped nested models
    name: str
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

    @model_validator(mode="before")
    @classmethod
    def organize_flat_data(cls, data: dict) -> dict:
        """Transform flat API response into nested structure."""
        if isinstance(data, dict) and "check_info" not in data:
            # This is a flat structure from the API, organize it
            return {
                # Core fields
                "name": data.get("name"),
                # Check info
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
                # State history
                "state_history": {
                    "state": data.get("state"),
                    "last_state": data.get("last_state"),
                    "last_state_change": data.get("last_state_change"),
                    "previous_hard_state": data.get("previous_hard_state"),
                },
                # Flapping info
                "flapping_info": {
                    "is_flapping": data.get("is_flapping"),
                    "flap_detection_enabled": data.get("flap_detection_enabled"),
                    "flappiness": data.get("flappiness"),
                    "low_flap_threshold": data.get("low_flap_threshold"),
                    "percent_state_change": data.get("percent_state_change"),
                },
                # Notification info
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
                # Performance info
                "performance_info": {
                    "execution_time": data.get("execution_time"),
                    "latency": data.get("latency"),
                    "metrics": data.get("metrics"),
                    "perf_data": data.get("perf_data"),
                    "performance_data": data.get("performance_data"),
                    "pnpgraph_present": data.get("pnpgraph_present"),
                    "process_performance_data": data.get("process_performance_data"),
                },
                # Output info
                "output_info": {
                    "plugin_output": data.get("plugin_output"),
                    "long_plugin_output": data.get("long_plugin_output"),
                },
                # Downtime/comment info
                "downtime_comment_info": {
                    "comments_with_extra_info": data.get("comments_with_extra_info"),
                    "downtimes_with_extra_info": data.get("downtimes_with_extra_info"),
                    "pending_flex_downtime": data.get("pending_flex_downtime"),
                    "scheduled_downtime_depth": data.get("scheduled_downtime_depth"),
                },
                # Custom data
                "custom_data": {
                    "custom_variable_names": data.get("custom_variable_names"),
                    "custom_variable_values": data.get("custom_variable_values"),
                    "custom_variables": data.get("custom_variables"),
                    "labels": data.get("labels"),
                    "tags": data.get("tags"),
                },
                # Notes info
                "notes_info": {
                    "notes": data.get("notes"),
                    "notes_expanded": data.get("notes_expanded"),
                    "notes_url": data.get("notes_url"),
                    "notes_url_expanded": data.get("notes_url_expanded"),
                },
                # System info
                "system_info": {
                    "modified_attributes": data.get("modified_attributes"),
                    "modified_attributes_list": data.get("modified_attributes_list"),
                },
                "acknowledgement_info": {
                    "acknowledgement_type": data.get("acknowledgement_type"),
                    "acknowledged": data.get("acknowledged"),
                },
            }
        # Already in nested format
        return data


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
    def _ext(self) -> HostExtensions:
        return self.extensions

    @property
    def comments(self) -> List[Comment] | None:
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
    def state(self) -> Enum:
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
