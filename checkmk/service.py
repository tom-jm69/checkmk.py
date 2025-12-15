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
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

from .enums import ServiceStates
from .exceptions import ServiceNoProblemError, ServiceProblemAlreadyAcknowledgedError
from .models import (
    Acknowledgement,
    CheckInfo,
    Comment,
    CustomServiceData,
    DowntimeCommentInfo,
    FlappingInfo,
    Link,
    NotesInfo,
    NotificationInfo,
    PerformanceInfo,
    PluginOutputInfo,
    ServiceAcknowledgementRequest,
    ServiceComment,
    StateHistory,
    SystemInfo,
)
from .state import ConnectionState


class ServiceExtensions(BaseModel):
    """Service extensions with organized nested data models."""

    host_name: str
    description: str

    check_info: CheckInfo
    state_history: StateHistory
    flapping_info: FlappingInfo
    notification_info: NotificationInfo
    performance_info: PerformanceInfo
    output_info: PluginOutputInfo
    downtime_comment_info: DowntimeCommentInfo
    custom_data: CustomServiceData
    notes_info: NotesInfo
    system_info: SystemInfo
    acknowledgement_info: Acknowledgement

    @model_validator(mode="before")
    @classmethod
    def organize_flat_data(cls, data: dict) -> dict:
        """Transform flat API response into nested structure."""
        if isinstance(data, dict) and "check_info" not in data:
            return {
                "host_name": data.get("host_name"),
                "description": data.get("description"),
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
                    "host_tags": data.get("host_tags"),
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
                    "mk_inventory": data.get("mk_inventory"),
                    "mk_inventory_gz": data.get("mk_inventory_gz"),
                    "mk_inventory_last": data.get("mk_inventory_last"),
                    "mk_logwatch_files": data.get("mk_logwatch_files"),
                    "modified_attributes": data.get("modified_attributes"),
                    "modified_attributes_list": data.get("modified_attributes_list"),
                    "obsess_over_host": data.get("obsess_over_host"),
                    "parents": data.get("parents"),
                    "smartping_timeout": data.get("smartping_timeout"),
                },
                "acknowledgement_info": {
                    "acknowledgement_type": data.get("acknowledgement_type"),
                    "acknowledged": data.get("acknowledged"),
                },
            }
        return data


class Service(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    domain_type: str = Field(alias="domainType")
    id: str
    links: List[Link]
    members: Dict
    title: str
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    extensions: ServiceExtensions

    _state: ConnectionState = PrivateAttr()

    @property
    def _ext(self) -> ServiceExtensions:
        return self.extensions

    @property
    def comments(self) -> List[Comment] | None:
        return self._ext.downtime_comment_info.comments_with_extra_info

    @property
    def description(self) -> str:
        return self._ext.description

    @property
    def acknowledged(self) -> bool:
        return self._ext.acknowledgement_info.acknowledged

    @property
    def acknowledgement_type(self) -> int:
        return self._ext.acknowledgement_info.acknowledgement_type

    @property
    def last_check(self) -> datetime:
        return self._ext.check_info.last_check

    @property
    def host_name(self) -> str:
        return self._ext.host_name

    @property
    def state(self) -> Enum:
        return ServiceStates(self._ext.state_history.state)

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
    def host_tags(self) -> dict[str, str] | None:
        return self._ext.custom_data.host_tags

    async def acknowledge(
        self, comment: str, sticky: bool = True, persistent: bool = False, notify: bool = True
    ) -> bool:
        """
        Acknowledge this service.

        Args:
            comment: The acknowledgement comment
            sticky: Whether the acknowledgement is sticky
            persistent: Whether the acknowledgement persists across restarts
            notify: Whether to send notifications
        """
        if self.acknowledged:
            raise ServiceProblemAlreadyAcknowledgedError(service_description=self.description)

        if not self.problem:
            raise ServiceNoProblemError(service_description=self.description)

        data = ServiceAcknowledgementRequest(
            host_name=self.host_name,
            service_description=self.description,
            comment=comment,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )

        return await self._state.http.add_service_acknowledgement(data)

    async def add_comment(self, comment: str, persistent: bool = False) -> ServiceComment:
        """
        Add a comment to this host.

        Args:
            comment: The comment
            persistent: Whether the acknowledgement persists across restarts
        """
        data = ServiceComment(
            host_name=self.host_name,
            service_description=self.description,
            comment=comment,
            persistent=persistent,
        )
        await self._state.http.add_service_comment(data)
        return data

    async def add_downtime(
        self, start_time: datetime, end_time: datetime, comment: str, *, recurring: bool = False
    ) -> None: ...

    async def remove_acknowledgement(self) -> None: ...
