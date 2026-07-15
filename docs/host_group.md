# HostGroup

The `HostGroup` class represents a Checkmk host group with all its properties.

## Getting Host Groups

### From Client

```python
host_groups = await client.get_host_groups()
for group in host_groups:
    print(f"{group.name}: {group.num_hosts} hosts")
```

### A Single Host Group

```python
group = await client.get_host_group("my_group")
print(group.alias)
```

## Properties

### name
**Type:** `str`

The name of the host group.

### alias
**Type:** `str`

The alias of the host group.

### action_url / notes / notes_url
**Type:** `str | None`

Optional notes and action URL configured on the group.

### hosts
**Type:** `list[str] | None`

List of host names that are members of the group.

```python
if group.hosts:
    for host_name in group.hosts:
        print(host_name)
```

### hosts_with_state
**Type:** `List[HostMemberState] | None`

List of member hosts together with their state and check status.

```python
if group.hosts_with_state:
    for member in group.hosts_with_state:
        print(f"{member.host_name}: state={member.state}, checked={member.has_been_checked}")
```

### num_hosts / num_hosts_up / num_hosts_down / num_hosts_unreach / num_hosts_pending
**Type:** `int | None`

Host counts by state.

### num_hosts_handled_problems / num_hosts_unhandled_problems
**Type:** `int | None`

Counts of hosts with handled/unhandled problems.

### num_services / num_services_ok / num_services_warn / num_services_crit / num_services_unknown / num_services_pending
**Type:** `int | None`

Soft-state service counts across all hosts in the group.

### num_services_hard_ok / num_services_hard_warn / num_services_hard_crit / num_services_hard_unknown
**Type:** `int | None`

Hard-state service counts across all hosts in the group.

### num_services_handled_problems / num_services_unhandled_problems
**Type:** `int | None`

Counts of services with handled/unhandled problems.

### worst_host_state
**Type:** `HostStates`

The worst state of all hosts in the group.

```python
from checkmk.enums import HostStates

if group.worst_host_state == HostStates.DOWN:
    print(f"{group.name} has a down host")
```

### worst_service_state / worst_service_hard_state
**Type:** `ServiceStates`

The worst soft/hard service state of all hosts in the group.

## Complete Example

```python
import asyncio
from checkmk import Client, HostStates

async def check_host_groups():
    async with Client(...) as client:
        host_groups = await client.get_host_groups()

        for group in host_groups:
            print(f"\nGroup: {group.name} ({group.alias})")
            print(f"Hosts: {group.num_hosts} (up={group.num_hosts_up}, down={group.num_hosts_down})")

            if group.worst_host_state != HostStates.UP:
                print(f"  ⚠️  Worst host state: {group.worst_host_state}")

if __name__ == "__main__":
    asyncio.run(check_host_groups())
```
