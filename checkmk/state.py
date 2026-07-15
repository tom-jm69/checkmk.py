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


from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .http import CheckmkHTTP


class Identifiable(Protocol):
    """Anything cacheable by `ConnectionState`."""

    id: str


class ConnectionState:
    """Central state manager that holds shared resources"""

    def __init__(self, http: "CheckmkHTTP") -> None:
        self.http: "CheckmkHTTP" = http
        self._cache: dict[str, Identifiable] = {}

    def add_to_cache(self, obj: Identifiable) -> None:
        self._cache[obj.id] = obj

    def get_from_cache(self, obj_id: str) -> Identifiable | None:
        return self._cache.get(obj_id)
