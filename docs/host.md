# Host

The `Host` class represents a Checkmk host with all its properties and methods.

## Getting Hosts

### From Client

```python
hosts = await client.get_hosts()
for host in hosts:
    print(f"{host.name}: {host.state}")
```

## Properties

### name / host_name
**Type:** `str`

The name of the host.

```python
print(host.name)
print(host.host_name)  # Same as name
```

### state
**Type:** `HostStates` (Enum)

The current state of the host.

```python
from checkmk.enums import HostStates

if host.state == HostStates.UP:
    print("Host is up")
elif host.state == HostStates.DOWN:
    print("Host is down")

# Convert to int or string
print(int(host.state))  # 0 or 1
print(str(host.state))  # "UP" or "DOWN"
```

### problem
**Type:** `bool`

Indicates if the host has a problem (state != UP).

```python
if host.problem:
    print(f"Host {host.name} has a problem!")
```

### acknowledged
**Type:** `bool`

Indicates if the host's problem has been acknowledged.

```python
if host.problem and not host.acknowledged:
    await host.acknowledge(comment="Working on it")
```

### comments
**Type:** `List[Comment] | None`

List of comments on the host.

```python
if host.comments:
    for comment in host.comments:
        print(f"{comment.author}: {comment.comment}")
        print(f"Entry time: {comment.entry_time}")
```

### custom_variables
**Type:** `dict[str, str] | None`

Dictionary of custom variables assigned to the host.

```python
if host.custom_variables:
    for key, value in host.custom_variables.items():
        print(f"{key}: {value}")
```

### tags
**Type:** `dict[str, str] | None`

Dictionary of host tags.

```python
if host.tags:
    for key, value in host.tags.items():
        print(f"{key}: {value}")
```

## Methods

### acknowledge()

Acknowledge a host problem.

```python
await host.acknowledge(
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

**Raises:**
- `HostNoProblemError` - Host has no problem to acknowledge
- `HostProblemAlreadyAcknowledgedError` - Problem is already acknowledged

**Example:**
```python
try:
    await host.acknowledge(
        comment="Working on network issue",
        sticky=True,
        notify=True
    )
except HostProblemAlreadyAcknowledgedError:
    print("Already acknowledged")
except HostNoProblemError:
    print("Host has no problem")
```

### add_comment()

Add a comment to the host.

```python
await host.add_comment(
    comment: str,
    persistent: bool = True
)
```

**Parameters:**
- `comment` - The comment text (required)
- `persistent` - Whether the comment persists across restarts (default: `True`)

**Returns:** `HostComment`

**Example:**
```python
comment = await host.add_comment(
    comment="Scheduled maintenance tonight",
    persistent=True
)
```

### get_services()

Get all services for this host.

```python
services = await host.get_services()
```

**Returns:** `List[Service]`

**Example:**
```python
services = await host.get_services()
for service in services:
    print(f"  {service.description}: {service.state}")
```

## Complete Example

```python
import asyncio
from checkmk import Client, HostStates

async def check_hosts():
    async with Client(...) as client:
        hosts = await client.get_hosts()

        for host in hosts:
            print(f"\nHost: {host.name}")
            print(f"State: {host.state}")

            # Check if host has problems
            if host.problem:
                print("  ⚠️  Host has a problem!")

                if not host.acknowledged:
                    print("  Problem is not acknowledged")

                    # Acknowledge the problem
                    await host.acknowledge(
                        comment="Investigating the issue"
                    )
                    print("  ✓ Problem acknowledged")

            # Get services for this host
            services = await host.get_services()
            print(f"  Services: {len(services)}")

            # Show custom variables
            if host.custom_variables:
                print("  Custom variables:")
                for key, value in host.custom_variables.items():
                    print(f"    {key}: {value}")

if __name__ == "__main__":
    asyncio.run(check_hosts())
```
