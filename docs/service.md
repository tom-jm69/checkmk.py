# Service

The `Service` class represents a Checkmk service with all its properties and methods.

## Getting Services

### From Client

```python
services = await client.get_services()
for service in services:
    print(f"{service.host_name}/{service.description}: {service.state}")
```

### From Host

```python
host = hosts[0]
services = await host.get_services()
```

## Properties

### host_name
**Type:** `str`

The name of the host this service belongs to.

```python
print(service.host_name)
```

### description
**Type:** `str`

The service description.

```python
print(service.description)
```

### state
**Type:** `ServiceStates` (Enum)

The current state of the service.

```python
from checkmk.enums import ServiceStates

if service.state == ServiceStates.OK:
    print("Service is OK")
elif service.state == ServiceStates.WARNING:
    print("Service has a warning")
elif service.state == ServiceStates.CRITICAL:
    print("Service is critical")

# Convert to int or string
print(int(service.state))  # 0, 1, or 2
print(str(service.state))  # "OK", "WARNING", or "CRITICAL"
```

### problem
**Type:** `bool`

Indicates if the service has a problem (state != OK).

```python
if service.problem:
    print(f"Service {service.description} has a problem!")
```

### acknowledged
**Type:** `bool`

Indicates if the service's problem has been acknowledged.

```python
if service.problem and not service.acknowledged:
    await service.acknowledge(comment="Working on it")
```

### acknowledgement_type
**Type:** `int`

The type of acknowledgement.

```python
print(service.acknowledgement_type)
```

### last_check
**Type:** `datetime`

The datetime of the last check.

```python
print(f"Last checked: {service.last_check}")
```

### comments
**Type:** `List[Comment] | None`

List of comments on the service.

```python
if service.comments:
    for comment in service.comments:
        print(f"{comment.author}: {comment.comment}")
        print(f"Entry time: {comment.entry_time}")
```

### custom_variables
**Type:** `dict[str, str] | None`

Dictionary of custom variables assigned to the service.

```python
if service.custom_variables:
    for key, value in service.custom_variables.items():
        print(f"{key}: {value}")
```

### tags
**Type:** `dict[str, str] | None`

Dictionary of service tags.

```python
if service.tags:
    for key, value in service.tags.items():
        print(f"{key}: {value}")
```

### host_tags
**Type:** `dict[str, str] | None`

Dictionary of host tags (available for services).

```python
if service.host_tags:
    for key, value in service.host_tags.items():
        print(f"{key}: {value}")
```

## Methods

### acknowledge()

Acknowledge a service problem.

```python
await service.acknowledge(
    comment: str,
    sticky: bool = True,
    persistent: bool = False,
    notify: bool = True
)
```

**Parameters:**
- `comment` - The acknowledgement comment (required)
- `sticky` - Whether the acknowledgement is sticky (default: `True`)
- `persistent` - Whether the acknowledgement persists across restarts (default: `False`)
- `notify` - Whether to send notifications (default: `True`)

**Returns:** `bool`

**Raises:**
- `ServiceNoProblemError` - Service has no problem to acknowledge
- `ServiceProblemAlreadyAcknowledgedError` - Problem is already acknowledged

**Example:**
```python
try:
    await service.acknowledge(
        comment="Investigating high response time",
        sticky=True,
        notify=True
    )
except ServiceProblemAlreadyAcknowledgedError:
    print("Already acknowledged")
except ServiceNoProblemError:
    print("Service has no problem")
```

### add_comment()

Add a comment to the service.

```python
await service.add_comment(
    comment: str,
    persistent: bool = True
)
```

**Parameters:**
- `comment` - The comment text (required)
- `persistent` - Whether the comment persists across restarts (default: `True`)

**Returns:** `ServiceComment`

**Example:**
```python
comment = await service.add_comment(
    comment="Scheduled maintenance tonight",
    persistent=True
)
```

## Complete Example

```python
import asyncio
from checkmk import Client, ServiceStates

async def check_services():
    async with Client(...) as client:
        services = await client.get_services()

        # Find all services with problems
        problems = [s for s in services if s.problem]

        print(f"Found {len(problems)} services with problems")

        for service in problems:
            print(f"\n{service.host_name}/{service.description}")
            print(f"State: {service.state}")
            print(f"Last check: {service.last_check}")

            # Check if acknowledged
            if service.acknowledged:
                print("✓ Problem acknowledged")
            else:
                print("⚠️  Problem not acknowledged")

                # Acknowledge critical services
                if service.state == ServiceStates.CRITICAL:
                    await service.acknowledge(
                        comment="Auto-acknowledged critical service"
                    )
                    print("✓ Acknowledged")

            # Add a comment
            await service.add_comment(
                comment=f"Checked at {service.last_check}"
            )

if __name__ == "__main__":
    asyncio.run(check_services())
```

## Service States

The `ServiceStates` enum provides constants for service states:

```python
from checkmk.enums import ServiceStates

# Available states
ServiceStates.OK        # 0
ServiceStates.WARNING   # 1
ServiceStates.WARN      # 1 (alias for WARNING)
ServiceStates.CRITICAL  # 2

# Usage
if service.state == ServiceStates.CRITICAL:
    print("Service is critical!")

# Convert to string
print(str(service.state))  # "OK", "WARNING", or "CRITICAL"

# Convert to int
print(int(service.state))  # 0, 1, or 2
```
