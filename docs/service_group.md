# ServiceGroup

The `ServiceGroup` class represents a Checkmk service group with all its properties.

## Getting Service Groups

### From Client

```python
service_groups = await client.get_service_groups()
for group in service_groups:
    print(f"{group.name}: {group.num_services} services")
```

### A Single Service Group

```python
group = await client.get_service_group("my_group")
print(group.alias)
```

## Properties

### name
**Type:** `str`

The name of the service group.

### alias
**Type:** `str`

The alias of the service group.

### action_url / notes / notes_url
**Type:** `str | None`

Optional notes and action URL configured on the group.

### services
**Type:** `List[ServiceMember] | None`

List of host/service pairs that are members of the group.

```python
if group.services:
    for member in group.services:
        print(f"{member.host_name}/{member.service_description}")
```

### services_with_state
**Type:** `List[ServiceMemberState] | None`

List of member services together with their state and check status.

```python
if group.services_with_state:
    for member in group.services_with_state:
        print(f"{member.host_name}/{member.service_description}: state={member.state}")
```

### num_services / num_services_ok / num_services_warn / num_services_crit / num_services_unknown / num_services_pending
**Type:** `int | None`

Soft-state service counts in the group.

### num_services_hard_ok / num_services_hard_warn / num_services_hard_crit / num_services_hard_unknown
**Type:** `int | None`

Hard-state service counts in the group.

### num_services_handled_problems / num_services_unhandled_problems
**Type:** `int | None`

Counts of services with handled/unhandled problems.

### worst_service_state
**Type:** `ServiceStates`

The worst soft state of all services in the group.

```python
from checkmk.enums import ServiceStates

if group.worst_service_state == ServiceStates.CRITICAL:
    print(f"{group.name} has a critical service")
```

## Complete Example

```python
import asyncio
from checkmk import Client, ServiceStates

async def check_service_groups():
    async with Client(...) as client:
        service_groups = await client.get_service_groups()

        for group in service_groups:
            print(f"\nGroup: {group.name} ({group.alias})")
            print(f"Services: {group.num_services} (ok={group.num_services_ok}, crit={group.num_services_crit})")

            if group.worst_service_state == ServiceStates.CRITICAL:
                print("  ⚠️  Group has a critical service")

if __name__ == "__main__":
    asyncio.run(check_service_groups())
```
