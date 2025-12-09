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
from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .exceptions import ServiceNoProblemError, ServiceProblemAlreadyAcknowledgedError
from .models import Comment, Link, ServiceAcknowledgement, ServiceComment, normalize_comments
from .state import ConnectionState

if TYPE_CHECKING:
    from .host import Host


class ServiceExtensions(BaseModel):
    description: str
    host_name: str
    state: int
    acknowledged: Optional[int] = None
    acknowledgement_type: Optional[int] = None
    check_command: Optional[str] = None
    check_command_expanded: Optional[str] = None
    check_flapping_recovery_notification: Optional[int] = None
    check_freshness: Optional[int] = None
    check_interval: Optional[float] = None
    check_options: Optional[int] = None
    check_period: Optional[str] = None
    check_type: Optional[int] = None
    checks_enabled: Optional[int] = None
    comments_with_extra_info: Optional[List[Comment]] = None
    contact_groups: Optional[List] = None
    contacts: Optional[List] = None
    current_attempt: Optional[int] = None
    current_notification_number: Optional[int] = None
    custom_variable_names: Optional[List] = None
    custom_variable_values: Optional[List] = None
    custom_variables: Optional[Dict] = None
    display_name: Optional[str] = None
    downtimes: Optional[List] = None
    downtimes_with_extra_info: Optional[List] = None
    downtimes_with_info: Optional[List] = None
    event_handler: Optional[str] = None
    event_handler_enabled: Optional[int] = None
    execution_time: Optional[float] = None
    first_notification_delay: Optional[float] = None
    flap_detection_enabled: Optional[int] = None
    flappiness: Optional[float] = None
    groups: Optional[List] = None
    hard_state: Optional[int] = None
    has_been_checked: Optional[int] = None
    high_flap_threshold: Optional[float] = None

    # Extended fields
    icon_image: Optional[str] = None
    icon_image_alt: Optional[str] = None
    icon_image_expanded: Optional[str] = None
    in_check_period: Optional[int] = None
    in_notification_period: Optional[int] = None
    in_service_period: Optional[int] = None
    initial_state: Optional[int] = None
    is_executing: Optional[int] = None
    is_flapping: Optional[int] = None
    label_names: Optional[List[str]] = None
    label_source_names: Optional[List[str]] = None
    label_source_values: Optional[List[str]] = None
    label_sources: Optional[Dict] = None
    label_values: Optional[List[str]] = None
    labels: Optional[Dict[str, str]] = None
    last_check: Optional[datetime] = None
    last_hard_state: Optional[int] = None
    last_hard_state_change: Optional[int] = None
    last_notification: Optional[int] = None
    last_state: Optional[int] = None
    last_state_change: Optional[datetime] = None
    last_time_down: Optional[datetime] = None
    last_time_unreachable: Optional[datetime] = None
    last_time_up: Optional[datetime] = None
    latency: Optional[float] = None
    long_plugin_output: Optional[str] = None
    low_flap_threshold: Optional[float] = None
    max_check_attempts: Optional[int] = None
    metrics: Optional[List] = None
    mk_inventory: Optional[bytes] = None
    mk_inventory_gz: Optional[bytes] = None
    mk_inventory_last: Optional[int] = None
    mk_logwatch_files: Optional[List[str]] = None
    modified_attributes: Optional[int] = None
    modified_attributes_list: Optional[List[str]] = None
    next_check: Optional[datetime] = None
    next_notification: Optional[int] = None
    no_more_notifications: Optional[int] = None
    notes: Optional[str] = None
    notes_expanded: Optional[str] = None
    notes_url: Optional[str] = None
    notes_url_expanded: Optional[str] = None
    notification_interval: Optional[float] = None
    notification_period: Optional[str] = None
    notification_postponement_reason: Optional[str] = None
    notifications_enabled: Optional[int] = None
    obsess_over_host: Optional[int] = None
    parents: Optional[List[str]] = None
    pending_flex_downtime: Optional[int] = None
    percent_state_change: Optional[float] = None
    perf_data: Optional[str] = None
    performance_data: Optional[Dict[str, float]] = None
    plugin_output: Optional[str] = None
    pnpgraph_present: Optional[int] = None
    previous_hard_state: Optional[int] = None
    process_performance_data: Optional[int] = None
    retry_interval: Optional[float] = None
    scheduled_downtime_depth: Optional[int] = None
    service_period: Optional[str] = None
    services: Optional[List] = None
    services_with_fullstate: Optional[List] = None
    services_with_info: Optional[List] = None
    services_with_state: Optional[List] = None
    smartping_timeout: Optional[int] = None
    staleness: Optional[float] = None
    state_type: Optional[int] = None
    statusmap_image: Optional[str] = None
    structured_status: Optional[bytes] = None
    tag_names: Optional[List[str]] = None
    tag_values: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    total_services: Optional[int] = None
    worst_service_hard_state: Optional[int] = None
    worst_service_state: Optional[int] = None

    # we need to add validators
    @field_validator("comments_with_extra_info", mode="before")
    @classmethod
    def parse_comments(cls, v):
        return normalize_comments(v)


class Service(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    domain_type: str = Field(alias="domainType")
    id: str
    links: List[Link]
    members: Dict
    title: str
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    extensions: ServiceExtensions

    state: ConnectionState = Field(exclude=True, repr=False)

    @property
    def comments(self):
        return self.extensions.comments_with_extra_info

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
        if self.extensions.acknowledged:
            # problem already acknowledged
            raise ServiceProblemAlreadyAcknowledgedError(
                service_description=self.extensions.description
            )

        if not self.extensions.state:
            # we have no problem on this service if state is True
            raise ServiceNoProblemError(service_description=self.extensions.description)

        data = ServiceAcknowledgement(
            host_name=self.extensions.host_name,
            service_description=self.extensions.description,
            comment=comment,
            sticky=sticky,
            persistent=persistent,
            notify=notify,
        )

        return await self.state.http.add_service_acknowledgement(data)

    async def remove_acknowledgement(self) -> None:
        """
        Remove the acknowledgement from this service.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("Service acknowledgement removal is not yet implemented")

    async def add_comment(self, comment: str, persistent: bool = False) -> ServiceComment:
        """
        Add a comment to this host.

        Args:
            comment: The comment
            persistent: Whether the acknowledgement persists across restarts
        """
        data = ServiceComment(
            host_name=self.extensions.host_name,
            service_description=self.extensions.description,
            comment=comment,
            persistent=persistent,
        )
        await self.state.http.add_service_comment(data)
        return data

    async def add_downtime(
        self, start_time: datetime, end_time: datetime, comment: str, *, recurring: bool = False
    ) -> None:
        """
        Schedule downtime for this service.

        Args:
            start_time: When the downtime should start
            end_time: When the downtime should end
            comment: Comment explaining the reason for downtime
            recurring: Whether the downtime should recur

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("Service downtime scheduling is not yet implemented")
