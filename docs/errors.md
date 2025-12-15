# Error Handling

The library provides a comprehensive exception hierarchy for different types of errors.

## Exception Hierarchy

```
CheckmkException (Base)
├── FetchError
│   ├── HostFetchError
│   └── ServiceFetchError
├── ParseError
│   ├── HostParseError
│   └── ServiceParseError
├── ProblemAcknowledgementError
│   ├── HostNoProblemError
│   ├── HostProblemAlreadyAcknowledgedError
│   ├── ServiceNoProblemError
│   └── ServiceProblemAlreadyAcknowledgedError
└── HTTPError
    ├── Unauthorized (401)
    ├── Forbidden (403)
    ├── NotFound (404)
    ├── TooManyRequests (429)
    └── ServiceUnavailable (500+)
```

## Importing Exceptions

```python
from checkmk import (
    CheckmkException,           # Base exception
    HostException,              # Base host exception
    ServiceException,           # Base service exception
    HostFetchError,             # Error fetching hosts
    ServiceFetchError,          # Error fetching services
    HostParseError,             # Error parsing host data
    ServiceParseError,          # Error parsing service data
    HostNoProblemError,         # Host has no problem to acknowledge
    ServiceNoProblemError,      # Service has no problem to acknowledge
    HostProblemAlreadyAcknowledgedError,
    ServiceProblemAlreadyAcknowledgedError,
    HTTPError,                  # Base HTTP error
    Unauthorized,               # 401 error
    Forbidden,                  # 403 error
    NotFound,                   # 404 error
    TooManyRequests,           # 429 error
    ServiceUnavailable,        # 500+ errors
)
```

## Exception Details

### CheckmkException

Base exception for all Checkmk errors.

### FetchError

Base exception for data fetching errors.

#### HostFetchError

Raised when fetching hosts fails.

```python
try:
    hosts = await client.get_hosts()
except HostFetchError as e:
    print(f"Failed to fetch hosts: {e}")
```

#### ServiceFetchError

Raised when fetching services fails.

```python
try:
    services = await client.get_services()
except ServiceFetchError as e:
    print(f"Failed to fetch services: {e}")
```

### ParseError

Base exception for data parsing errors.

#### HostParseError

Raised when parsing host data fails.

```python
try:
    hosts = await client.get_hosts()
except HostParseError as e:
    print(f"Failed to parse host: {e}")
    print(f"Raw data: {e.raw_data}")
    print(f"Host name: {e.host_name}")
```

#### ServiceParseError

Raised when parsing service data fails.

```python
try:
    services = await client.get_services()
except ServiceParseError as e:
    print(f"Failed to parse service: {e}")
    print(f"Raw data: {e.raw_data}")
    print(f"Service: {e.service_description}")
```

### Problem Acknowledgement Errors

#### HostNoProblemError

Raised when attempting to acknowledge a host that has no problem.

```python
try:
    await host.acknowledge(comment="Working on it")
except HostNoProblemError:
    print(f"Host {host.name} has no problem to acknowledge")
```

#### HostProblemAlreadyAcknowledgedError

Raised when attempting to acknowledge a host problem that's already acknowledged.

```python
try:
    await host.acknowledge(comment="Working on it")
except HostProblemAlreadyAcknowledgedError:
    print(f"Host {host.name} problem already acknowledged")
```

#### ServiceNoProblemError

Raised when attempting to acknowledge a service that has no problem.

```python
try:
    await service.acknowledge(comment="Working on it")
except ServiceNoProblemError:
    print(f"Service {service.description} has no problem to acknowledge")
```

#### ServiceProblemAlreadyAcknowledgedError

Raised when attempting to acknowledge a service problem that's already acknowledged.

```python
try:
    await service.acknowledge(comment="Working on it")
except ServiceProblemAlreadyAcknowledgedError:
    print(f"Service {service.description} problem already acknowledged")
```

### HTTP Errors

#### Unauthorized (401)

Raised when authentication fails.

```python
try:
    hosts = await client.get_hosts()
except Unauthorized:
    print("Authentication failed. Check your credentials.")
```

#### Forbidden (403)

Raised when access is forbidden.

```python
try:
    await host.acknowledge(comment="Working on it")
except Forbidden:
    print("Access forbidden. Check your permissions.")
```

#### NotFound (404)

Raised when a resource is not found.

```python
try:
    response = await client.http.get_service(
        host_name="nonexistent",
        service_description="test"
    )
except NotFound:
    print("Service not found")
```

#### TooManyRequests (429)

Raised when rate limit is exceeded (after retries).

```python
try:
    hosts = await client.get_hosts()
except TooManyRequests:
    print("Rate limit exceeded")
```

#### ServiceUnavailable (500+)

Raised when the server is unavailable (after retries).

```python
try:
    hosts = await client.get_hosts()
except ServiceUnavailable:
    print("Server is unavailable")
```

## Error Handling Examples

### Handle Specific Errors

```python
async def safe_acknowledge(host):
    try:
        await host.acknowledge(comment="Working on it")
        print(f"✓ Acknowledged {host.name}")
    except HostProblemAlreadyAcknowledgedError:
        print(f"- {host.name} already acknowledged")
    except HostNoProblemError:
        print(f"- {host.name} has no problem")
    except Forbidden:
        print(f"✗ No permission to acknowledge {host.name}")
    except CheckmkException as e:
        print(f"✗ Error acknowledging {host.name}: {e}")
```

### Catch All Checkmk Errors

```python
try:
    hosts = await client.get_hosts()
    for host in hosts:
        if host.problem:
            await host.acknowledge(comment="Working on it")
except CheckmkException as e:
    print(f"Checkmk error: {e}")
```

### Handle HTTP Errors

```python
from checkmk import HTTPError, Unauthorized, Forbidden

try:
    hosts = await client.get_hosts()
except Unauthorized:
    print("Authentication failed")
except Forbidden:
    print("Access denied")
except HTTPError as e:
    print(f"HTTP error: {e.status} {e.message}")
```

### Retry on Specific Errors

```python
import asyncio
from checkmk import ServiceUnavailable, TooManyRequests

async def fetch_hosts_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await client.get_hosts()
        except (ServiceUnavailable, TooManyRequests) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise
```
