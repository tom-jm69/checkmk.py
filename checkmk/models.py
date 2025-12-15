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
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


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


def normalize_comments(v):
    if v is None:
        return v

    if isinstance(v, list) and v and isinstance(v[0], Comment):
        return v

    return [Comment.parse(row) for row in v]


class Link(BaseModel):
    domain_type: Optional[str] = Field(default=None, alias="domainType")
    href: HttpUrl
    method: str
    rel: str
    title: Optional[str] = None
    type: str


class ColumnsRequest(BaseModel):
    """Request model for columns query"""

    columns: List[str]


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


class Comment(BaseModel):
    id: int
    author: str
    comment: str
    entry_type: int
    entry_time: datetime

    @classmethod
    def parse(cls, row: list) -> "Comment":
        """
        Parse a single raw row:
        [id, author, comment, entry_type, unix_timestamp]
        """
        return cls(
            id=row[0],
            author=row[1],
            comment=row[2],
            entry_type=row[3],
            entry_time=row[4],
        )


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
    max_check_attempts: Optional[int] = None
    next_check: Optional[datetime] = None
    retry_interval: Optional[float] = None


class StateHistory(BaseModel):
    """Historical state tracking information."""

    state: int
    last_state: int
    last_state_change: Optional[datetime] = None
    previous_hard_state: Optional[int] = None


class FlappingInfo(BaseModel):
    """Flapping detection and monitoring."""

    is_flapping: bool
    flap_detection_enabled: Optional[int] = None
    flappiness: Optional[float] = None
    low_flap_threshold: Optional[float] = None
    percent_state_change: Optional[float] = None


class NotificationInfo(BaseModel):
    """Notification configuration and status."""

    first_notification_delay: Optional[float] = None
    next_notification: Optional[datetime] = None
    no_more_notifications: Optional[int] = None
    notification_interval: Optional[float] = None
    notification_period: Optional[str] = None
    notification_postponement_reason: Optional[str] = None
    notifications_enabled: Optional[int] = None


class Acknowledgement(BaseModel):
    """Checkmk acknowledgement data"""

    acknowledged: bool
    acknowledgement_type: int


class SystemInfo(BaseModel):
    """Advanced CheckMK system fields."""

    modified_attributes: Optional[int] = None
    modified_attributes_list: Optional[List[str]] = None


class NotesInfo(BaseModel):
    """Documentation and notes."""

    notes: Optional[str] = None
    notes_expanded: Optional[str] = None
    notes_url: Optional[str] = None
    notes_url_expanded: Optional[str] = None


class CustomServiceData(BaseModel):
    """Custom variables, tags, and labels."""

    custom_variable_names: Optional[List] = None
    custom_variable_values: Optional[List] = None
    custom_variables: Optional[Dict] = None
    host_tags: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    tags: Optional[Dict[str, str]] = None


class CustomHostData(BaseModel):
    """Custom variables, tags, and labels."""

    custom_variable_names: Optional[List] = None
    custom_variable_values: Optional[List] = None
    custom_variables: Optional[Dict] = None
    labels: Optional[Dict[str, str]] = None
    tags: Optional[Dict[str, str]] = None


class DowntimeCommentInfo(BaseModel):
    """Downtime and comment tracking."""

    comments_with_extra_info: Optional[List[Comment]] = None
    downtimes_with_extra_info: Optional[List] = None
    pending_flex_downtime: Optional[int] = None
    scheduled_downtime_depth: Optional[int] = None

    @field_validator("comments_with_extra_info", mode="before")
    @classmethod
    def parse_comments(cls, v):
        return normalize_comments(v)


class PluginOutputInfo(BaseModel):
    """Plugin output and messages."""

    plugin_output: Optional[str] = None
    long_plugin_output: Optional[str] = None


class PerformanceInfo(BaseModel):
    """Performance metrics and monitoring data."""

    execution_time: Optional[float] = None
    latency: Optional[float] = None
    metrics: Optional[List] = None
    perf_data: Optional[str] = None
    performance_data: Optional[Dict[str, float]] = None
    pnpgraph_present: Optional[int] = None
    process_performance_data: Optional[int] = None


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

    @classmethod
    def get_columns(cls, additional_fields: Optional[List[str]] = None) -> List[str]:
        """
        Returns the list of columns to request from the Checkmk API.

        Extracts field names from all nested model classes to ensure we request
        all necessary data from the API.

        Args:
            additional_fields: Include additional fields 

        Returns:
            Sorted list of column names
        """
        columns = set()

        if additional_fields:
            # Core fields for service queries
            columns.update(additional_fields)

        # Extract fields from all nested models
        for field_name, field_info in cls.__pydantic_fields__.items():
            model_class = field_info.annotation
            if hasattr(model_class, "__pydantic_fields__"):
                columns.update(model_class.__pydantic_fields__.keys())

        return sorted(columns)


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

    @classmethod
    def get_columns(cls, additional_fields: Optional[List[str]] = None) -> List[str]:
        """
        Returns the list of columns to request from the Checkmk API.

        Extracts field names from all nested model classes to ensure we request
        all necessary data from the API.

        Args:
            additional_fields: Include additional fields 

        Returns:
            Sorted list of column names
        """
        columns = set()

        if additional_fields:
            # Core fields for service queries
            columns.update(additional_fields)

        # Extract fields from all nested models
        for field_name, field_info in cls.__pydantic_fields__.items():
            model_class = field_info.annotation
            if hasattr(model_class, "__pydantic_fields__"):
                columns.update(model_class.__pydantic_fields__.keys())

        return sorted(columns)
