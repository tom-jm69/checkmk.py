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
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

Row = list[str | int | bool | None]


class APIAuth(BaseModel):
    """API authentication model"""

    username: str
    secret: str

    def to_header(self) -> str:
        """Convert to authorization header value"""
        import base64

        credentials = f"{self.username}:{self.secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"


class Link(BaseModel):
    domain_type: str | None = Field(default=None, alias="domainType")
    href: HttpUrl
    method: str
    rel: str
    title: str | None = None
    type: str


class ColumnsRequest(BaseModel):
    """Request model for columns query"""

    columns: list[str]


class HostComment(BaseModel):
    """Model for adding a host comment"""

    host_name: str
    comment: str
    persistent: bool = True
    comment_type: Literal["host"] = "host"


class ServiceComment(BaseModel):
    """Model for adding a service comment"""

    host_name: str
    service_description: str
    comment: str
    persistent: bool = True
    comment_type: Literal["service"] = "service"


class HostAcknowledgement(BaseModel):
    """Model for acknowledging a host problem"""

    host_name: str
    sticky: bool = True
    persistent: bool = False
    notify: bool = True
    comment: str
    acknowledge_type: Literal["host"] = "host"


class ServiceAcknowledgementRequest(BaseModel):
    """Model for acknowledging a service problem"""

    host_name: str
    service_description: str
    sticky: bool = True
    persistent: bool = False
    notify: bool = True
    comment: str
    acknowledge_type: Literal["service"] = "service"


class Group(BaseModel):
    groups: list[str]


class Comment(BaseModel):
    id: int
    author: str
    comment: str
    entry_type: int
    entry_time: datetime

    @classmethod
    def parse(cls, row: Row) -> "Comment":
        """
        Parse a single raw row:
        [id, author, comment, entry_type, unix_timestamp]
        """
        return cls(
            id=row[0],  # pyright: ignore[reportArgumentType]
            author=row[1],  # pyright: ignore[reportArgumentType]
            comment=row[2],  # pyright: ignore[reportArgumentType]
            entry_type=row[3],  # pyright: ignore[reportArgumentType]
            entry_time=row[4],  # pyright: ignore[reportArgumentType]
        )


def normalize_comments(v: list[Comment] | list[Row] | None) -> list[Comment] | None:
    if v is None:
        return v

    if v and isinstance(v[0], Comment):
        return v  # pyright: ignore[reportReturnType]

    return [Comment.parse(row) for row in v]  # pyright: ignore[reportArgumentType]


class CheckInfo(BaseModel):
    """Information about check configuration and execution."""

    check_command: str
    check_command_expanded: str
    check_flapping_recovery_notification: int
    check_freshness: int
    check_interval: float
    check_options: int
    check_period: str
    check_type: int
    checks_enabled: bool
    has_been_checked: bool
    is_executing: bool
    last_check: datetime
    max_check_attempts: int | None = None
    next_check: datetime | None = None
    retry_interval: float | None = None


class StateHistory(BaseModel):
    """Historical state tracking information."""

    state: int
    last_state: int
    last_state_change: datetime | None = None
    previous_hard_state: int | None = None


class FlappingInfo(BaseModel):
    """Flapping detection and monitoring."""

    is_flapping: bool
    flap_detection_enabled: int | None = None
    flappiness: float | None = None
    low_flap_threshold: float | None = None
    percent_state_change: float | None = None


class NotificationInfo(BaseModel):
    """Notification configuration and status."""

    first_notification_delay: float | None = None
    next_notification: datetime | None = None
    no_more_notifications: int | None = None
    notification_interval: float | None = None
    notification_period: str | None = None
    notification_postponement_reason: str | None = None
    notifications_enabled: int | None = None


class Acknowledgement(BaseModel):
    """Checkmk acknowledgement data"""

    acknowledged: bool
    acknowledgement_type: int


class SystemInfo(BaseModel):
    """Advanced CheckMK system fields."""

    modified_attributes: int | None = None
    modified_attributes_list: list[str] | None = None


class NotesInfo(BaseModel):
    """Documentation and notes."""

    notes: str | None = None
    notes_expanded: str | None = None
    notes_url: str | None = None
    notes_url_expanded: str | None = None


class CustomServiceData(BaseModel):
    """Custom variables, tags, and labels."""

    custom_variable_names: list[str] | None = None
    custom_variable_values: list[str] | None = None
    custom_variables: dict[str, str] | None = None
    host_tags: dict[str, str] | None = None
    labels: dict[str, str] | None = None
    tags: dict[str, str] | None = None


class CustomHostData(BaseModel):
    """Custom variables, tags, and labels."""

    custom_variable_names: list[str] | None = None
    custom_variable_values: list[str] | None = None
    custom_variables: dict[str, str] | None = None
    labels: dict[str, str] | None = None
    tags: dict[str, str] | None = None


class DowntimeCommentInfo(BaseModel):
    """Downtime and comment tracking."""

    comments_with_extra_info: list[Comment] | None = None
    downtimes_with_extra_info: list[object] | None = None
    pending_flex_downtime: int | None = None
    scheduled_downtime_depth: int | None = None

    @field_validator("comments_with_extra_info", mode="before")
    @classmethod
    def parse_comments(cls, v: list[Comment] | list[Row] | None) -> list[Comment] | None:
        return normalize_comments(v)


class PluginOutputInfo(BaseModel):
    """Plugin output and messages."""

    plugin_output: str | None = None
    long_plugin_output: str | None = None


class PerformanceInfo(BaseModel):
    """Performance metrics and monitoring data."""

    execution_time: float | None = None
    latency: float | None = None
    metrics: list[object] | None = None
    perf_data: str | None = None
    performance_data: dict[str, float] | None = None
    pnpgraph_present: int | None = None
    process_performance_data: int | None = None


class CheckmkServiceColumns(BaseModel):
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
    groups: Group

    @classmethod
    def get_columns(cls, additional_fields: list[str] | None = None) -> list[str]:
        """
        Returns the list of columns to request from the Checkmk API.

        Extracts field names from all nested model classes to ensure we request
        all necessary data from the API.

        Args:
            additional_fields: Include additional fields

        Returns:
            Sorted list of column names
        """
        columns: set[str] = set()

        if additional_fields:
            # Core fields for service queries
            columns.update(additional_fields)

        # Extract fields from all nested models
        for field_info in cls.__pydantic_fields__.values():
            model_class = field_info.annotation
            if model_class is not None and issubclass(model_class, BaseModel):
                columns.update(model_class.__pydantic_fields__.keys())

        return sorted(columns)


class HostMemberState(BaseModel):
    """A host group member together with its state and check status."""

    host_name: str
    state: int
    has_been_checked: bool

    @classmethod
    def parse(cls, row: Row) -> "HostMemberState":
        """
        Parse a single raw row:
        [host_name, state, has_been_checked]
        """
        return cls(
            host_name=row[0],  # pyright: ignore[reportArgumentType]
            state=row[1],  # pyright: ignore[reportArgumentType]
            has_been_checked=bool(row[2]),
        )


class ServiceMember(BaseModel):
    """A service group member identified by its host/service pair."""

    host_name: str
    service_description: str

    @classmethod
    def parse(cls, row: Row) -> "ServiceMember":
        """
        Parse a single raw row:
        [host_name, service_description]
        """
        return cls(
            host_name=row[0],  # pyright: ignore[reportArgumentType]
            service_description=row[1],  # pyright: ignore[reportArgumentType]
        )


class ServiceMemberState(BaseModel):
    """A service group member together with its state and check status."""

    host_name: str
    service_description: str
    state: int
    has_been_checked: bool

    @classmethod
    def parse(cls, row: Row) -> "ServiceMemberState":
        """
        Parse a single raw row:
        [host_name, service_description, state, has_been_checked]
        """
        return cls(
            host_name=row[0],  # pyright: ignore[reportArgumentType]
            service_description=row[1],  # pyright: ignore[reportArgumentType]
            state=row[2],  # pyright: ignore[reportArgumentType]
            has_been_checked=bool(row[3]),
        )


def normalize_host_members_with_state(
    v: list[HostMemberState] | list[Row] | None,
) -> list[HostMemberState] | None:
    if v is None:
        return v
    if v and isinstance(v[0], HostMemberState):
        return v  # pyright: ignore[reportReturnType]
    return [HostMemberState.parse(row) for row in v]  # pyright: ignore[reportArgumentType]


def normalize_service_members(
    v: list[ServiceMember] | list[Row] | None,
) -> list[ServiceMember] | None:
    if v is None:
        return v
    if v and isinstance(v[0], ServiceMember):
        return v  # pyright: ignore[reportReturnType]
    return [ServiceMember.parse(row) for row in v]  # pyright: ignore[reportArgumentType]


def normalize_service_members_with_state(
    v: list[ServiceMemberState] | list[Row] | None,
) -> list[ServiceMemberState] | None:
    if v is None:
        return v
    if v and isinstance(v[0], ServiceMemberState):
        return v  # pyright: ignore[reportReturnType]
    return [ServiceMemberState.parse(row) for row in v]  # pyright: ignore[reportArgumentType]


class HostGroupExtensions(BaseModel):
    """Extensions for a host group, matching the Checkmk Hostgroups Table."""

    name: str
    alias: str
    action_url: str | None = None
    notes: str | None = None
    notes_url: str | None = None
    members: list[str] | None = None
    members_with_state: list[HostMemberState] | None = None
    num_hosts: int | None = None
    num_hosts_down: int | None = None
    num_hosts_handled_problems: int | None = None
    num_hosts_pending: int | None = None
    num_hosts_unhandled_problems: int | None = None
    num_hosts_unreach: int | None = None
    num_hosts_up: int | None = None
    num_services: int | None = None
    num_services_crit: int | None = None
    num_services_handled_problems: int | None = None
    num_services_hard_crit: int | None = None
    num_services_hard_ok: int | None = None
    num_services_hard_unknown: int | None = None
    num_services_hard_warn: int | None = None
    num_services_ok: int | None = None
    num_services_pending: int | None = None
    num_services_unhandled_problems: int | None = None
    num_services_unknown: int | None = None
    num_services_warn: int | None = None
    worst_host_state: int | None = None
    worst_service_hard_state: int | None = None
    worst_service_state: int | None = None

    @field_validator("members_with_state", mode="before")
    @classmethod
    def parse_members_with_state(
        cls, v: list[HostMemberState] | list[Row] | None
    ) -> list[HostMemberState] | None:
        return normalize_host_members_with_state(v)


class ServiceGroupExtensions(BaseModel):
    """Extensions for a service group, matching the Checkmk Servicegroups Table."""

    name: str
    alias: str
    action_url: str | None = None
    notes: str | None = None
    notes_url: str | None = None
    members: list[ServiceMember] | None = None
    members_with_state: list[ServiceMemberState] | None = None
    num_services: int | None = None
    num_services_crit: int | None = None
    num_services_handled_problems: int | None = None
    num_services_hard_crit: int | None = None
    num_services_hard_ok: int | None = None
    num_services_hard_unknown: int | None = None
    num_services_hard_warn: int | None = None
    num_services_ok: int | None = None
    num_services_pending: int | None = None
    num_services_unhandled_problems: int | None = None
    num_services_unknown: int | None = None
    num_services_warn: int | None = None
    worst_service_state: int | None = None

    @field_validator("members", mode="before")
    @classmethod
    def parse_members(
        cls, v: list[ServiceMember] | list[Row] | None
    ) -> list[ServiceMember] | None:
        return normalize_service_members(v)

    @field_validator("members_with_state", mode="before")
    @classmethod
    def parse_members_with_state(
        cls, v: list[ServiceMemberState] | list[Row] | None
    ) -> list[ServiceMemberState] | None:
        return normalize_service_members_with_state(v)


class CheckmkHostColumns(BaseModel):
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

    @classmethod
    def get_columns(cls, additional_fields: list[str] | None = None) -> list[str]:
        """
        Returns the list of columns to request from the Checkmk API.

        Extracts field names from all nested model classes to ensure we request
        all necessary data from the API.

        Args:
            additional_fields: Include additional fields

        Returns:
            Sorted list of column names
        """
        columns: set[str] = set()

        if additional_fields:
            # Core fields for service queries
            columns.update(additional_fields)

        # Extract fields from all nested models
        for field_info in cls.__pydantic_fields__.values():
            model_class = field_info.annotation
            if model_class is not None and issubclass(model_class, BaseModel):
                columns.update(model_class.__pydantic_fields__.keys())
        return sorted(columns)
