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

from typing import List, Optional

from pydantic import BaseModel


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


class ColumnsRequest(BaseModel):
    """Request model for columns query"""
    columns: List[str]


class HostComment(BaseModel):
    """Model for adding a host comment"""
    host_name: str
    comment: str
    persistent: bool = True
    author: Optional[str] = None


class ServiceComment(BaseModel):
    """Model for adding a service comment"""
    host_name: str
    service_description: str
    comment: str
    persistent: bool = True
    author: Optional[str] = None


class HostAcknowledgement(BaseModel):
    """Model for acknowledging a host problem"""
    host_name: str
    sticky: bool = True
    persistent: bool = False
    notify: bool = True
    comment: str
    author: Optional[str] = None


class ServiceAcknowledgement(BaseModel):
    """Model for acknowledging a service problem"""
    host_name: str
    service_description: str
    sticky: bool = True
    persistent: bool = False
    notify: bool = True
    comment: str
    author: Optional[str] = None
