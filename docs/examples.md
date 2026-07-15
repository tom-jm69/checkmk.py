# Examples

This page contains practical examples for common use cases.

## Basic Examples

### List All Hosts and Services

```python
import asyncio
from checkmk import Client

async def list_all():
    async with Client(
        url="checkmk.example.com",
        site_name="mysite",
        username="automation",
        secret="your-api-secret",
    ) as client:
        # Get all hosts
        hosts = await client.get_hosts()
        print(f"Found {len(hosts)} hosts:")
        for host in hosts:
            print(f"  {host.name}: {host.state}")

        # Get all services
        services = await client.get_services()
        print(f"\nFound {len(services)} services:")
        for service in services:
            print(f"  {service.host_name}/{service.description}: {service.state}")

if __name__ == "__main__":
    asyncio.run(list_all())
```

### Check Hosts with Problems

```python
import asyncio
from checkmk import Client

async def check_problems():
    async with Client(...) as client:
        hosts = await client.get_hosts()

        problem_hosts = [h for h in hosts if h.problem]

        if problem_hosts:
            print(f"Found {len(problem_hosts)} hosts with problems:")
            for host in problem_hosts:
                status = "ACK" if host.acknowledged else "NEW"
                print(f"  [{status}] {host.name}: {host.state}")
        else:
            print("All hosts are up!")

if __name__ == "__main__":
    asyncio.run(check_problems())
```

## Monitoring Examples

### Monitor Services in WARNING or CRITICAL State

```python
import asyncio
from checkmk import Client, ServiceStates

async def monitor_services():
    async with Client(...) as client:
        services = await client.get_services()

        # Find unacknowledged problems
        problems = [
            s for s in services
            if s.problem and not s.acknowledged
        ]

        if problems:
            print(f"⚠️  Found {len(problems)} unacknowledged service problems:\n")

            for service in problems:
                icon = "🔴" if service.state == ServiceStates.CRITICAL else "🟡"
                print(f"{icon} {service.host_name}/{service.description}")
                print(f"   State: {service.state}")
                print(f"   Last check: {service.last_check}")
                print()
        else:
            print("✓ All services are OK or acknowledged")

if __name__ == "__main__":
    asyncio.run(monitor_services())
```

### Check Host and Its Services

```python
import asyncio
from checkmk import Client

async def check_host_services(host_name: str):
    async with Client(...) as client:
        hosts = await client.get_hosts()

        # Find the host
        host = next((h for h in hosts if h.name == host_name), None)
        if not host:
            print(f"Host {host_name} not found")
            return

        print(f"Host: {host.name} ({host.state})")

        # Get services for this host
        services = await host.get_services()
        print(f"Services: {len(services)}")

        for service in services:
            icon = "✓" if service.state == ServiceStates.OK else "✗"
            print(f"  {icon} {service.description}: {service.state}")

if __name__ == "__main__":
    asyncio.run(check_host_services("myhost"))
```

## Group Examples

### List Host and Service Groups with Their Worst State

```python
import asyncio
from checkmk import Client, HostStates, ServiceStates

async def list_groups():
    async with Client(...) as client:
        host_groups = await client.get_host_groups()
        print(f"Found {len(host_groups)} host groups:")
        for group in host_groups:
            flag = "⚠️" if group.worst_host_state != HostStates.UP else "✓"
            print(f"  {flag} {group.name}: {group.num_hosts} hosts")

        service_groups = await client.get_service_groups()
        print(f"\nFound {len(service_groups)} service groups:")
        for group in service_groups:
            flag = "⚠️" if group.worst_service_state != ServiceStates.OK else "✓"
            print(f"  {flag} {group.name}: {group.num_services} services")

if __name__ == "__main__":
    asyncio.run(list_groups())
```

### Find Which Groups a Host or Service Belongs To

```python
import asyncio
from checkmk import Client

async def check_membership(host_name: str):
    async with Client(...) as client:
        hosts = await client.get_hosts()
        host = next((h for h in hosts if h.name == host_name), None)
        if not host:
            print(f"Host {host_name} not found")
            return

        groups = await host.get_groups()
        print(f"{host.name} belongs to {len(groups)} host group(s):")
        for group in groups:
            print(f"  {group.name} ({group.alias})")

        for service in await host.get_services():
            service_groups = await service.get_groups()
            if service_groups:
                print(f"\n{service.description} belongs to:")
                for group in service_groups:
                    print(f"  {group.name} ({group.alias})")

if __name__ == "__main__":
    asyncio.run(check_membership("myhost"))
```

## Acknowledgement Examples

### Acknowledge All Unacknowledged Host Problems

```python
import asyncio
from checkmk import Client, HostProblemAlreadyAcknowledgedError, HostNoProblemError

async def acknowledge_all_hosts():
    async with Client(...) as client:
        hosts = await client.get_hosts()

        for host in hosts:
            if host.problem and not host.acknowledged:
                try:
                    await host.acknowledge(
                        comment="Automatically acknowledged by monitoring script",
                        sticky=True,
                        notify=False
                    )
                    print(f"✓ Acknowledged {host.name}")
                except HostProblemAlreadyAcknowledgedError:
                    print(f"- {host.name} already acknowledged")
                except HostNoProblemError:
                    print(f"- {host.name} has no problem")

if __name__ == "__main__":
    asyncio.run(acknowledge_all_hosts())
```

### Acknowledge Critical Services Only

```python
import asyncio
from checkmk import Client, ServiceStates

async def acknowledge_critical_services():
    async with Client(...) as client:
        services = await client.get_services()

        # Find critical, unacknowledged services
        critical = [
            s for s in services
            if s.state == ServiceStates.CRITICAL and not s.acknowledged
        ]

        print(f"Found {len(critical)} critical services")

        for service in critical:
            try:
                await service.acknowledge(
                    comment="Auto-acknowledged critical service",
                    sticky=True
                )
                print(f"✓ {service.host_name}/{service.description}")
            except Exception as e:
                print(f"✗ {service.host_name}/{service.description}: {e}")

if __name__ == "__main__":
    asyncio.run(acknowledge_critical_services())
```

## Comment Examples

### Add Comments to All Problem Services

```python
import asyncio
from checkmk import Client

async def add_comments():
    async with Client(...) as client:
        services = await client.get_services()

        problems = [s for s in services if s.problem]

        for service in problems:
            await service.add_comment(
                comment=f"Service in {service.state} state - under investigation",
                persistent=True
            )
            print(f"✓ Added comment to {service.host_name}/{service.description}")

if __name__ == "__main__":
    asyncio.run(add_comments())
```

### Read Comments from Hosts

```python
import asyncio
from checkmk import Client

async def read_comments():
    async with Client(...) as client:
        hosts = await client.get_hosts()

        for host in hosts:
            if host.comments:
                print(f"\n{host.name}:")
                for comment in host.comments:
                    print(f"  [{comment.entry_time}] {comment.author}")
                    print(f"  {comment.comment}")

if __name__ == "__main__":
    asyncio.run(read_comments())
```

## Advanced Examples

### Iterate Through Hosts and Services

```python
import asyncio
from checkmk import Client, ServiceStates

async def iterate_all():
    async with Client(...) as client:
        hosts = await client.get_hosts()

        for host in hosts:
            print(f"\n{'='*60}")
            print(f"Host: {host.name} ({host.state})")

            if host.custom_variables:
                print("Custom variables:")
                for key, value in host.custom_variables.items():
                    print(f"  {key}: {value}")

            # Get services for this host
            services = await host.get_services()
            print(f"\nServices ({len(services)}):")

            for service in services:
                icon = "✓" if service.state == ServiceStates.OK else "✗"
                print(f"  {icon} {service.description}: {service.state}")

                if service.problem and not service.acknowledged:
                    print(f"     ⚠️  Unacknowledged problem!")

if __name__ == "__main__":
    asyncio.run(iterate_all())
```

### Filter Services by Custom Variables

```python
import asyncio
from checkmk import Client

async def filter_by_custom_vars():
    async with Client(...) as client:
        services = await client.get_services()

        # Filter services with specific custom variable
        filtered = [
            s for s in services
            if s.custom_variables
            and s.custom_variables.get("ENVIRONMENT") == "production"
        ]

        print(f"Found {len(filtered)} production services:")
        for service in filtered:
            print(f"  {service.host_name}/{service.description}")

if __name__ == "__main__":
    asyncio.run(filter_by_custom_vars())
```

### Generate Status Report

```python
import asyncio
from checkmk import Client, HostStates, ServiceStates

async def status_report():
    async with Client(...) as client:
        hosts = await client.get_hosts()
        services = await client.get_services()

        # Host statistics
        hosts_up = sum(1 for h in hosts if h.state == HostStates.UP)
        hosts_down = sum(1 for h in hosts if h.state == HostStates.DOWN)
        hosts_ack = sum(1 for h in hosts if h.acknowledged)

        # Service statistics
        services_ok = sum(1 for s in services if s.state == ServiceStates.OK)
        services_warning = sum(1 for s in services if s.state == ServiceStates.WARNING)
        services_critical = sum(1 for s in services if s.state == ServiceStates.CRITICAL)
        services_ack = sum(1 for s in services if s.acknowledged)

        # Print report
        print("=" * 60)
        print("CHECKMK STATUS REPORT")
        print("=" * 60)
        print(f"\nHosts:")
        print(f"  Total: {len(hosts)}")
        print(f"  Up: {hosts_up}")
        print(f"  Down: {hosts_down}")
        print(f"  Acknowledged: {hosts_ack}")

        print(f"\nServices:")
        print(f"  Total: {len(services)}")
        print(f"  OK: {services_ok}")
        print(f"  Warning: {services_warning}")
        print(f"  Critical: {services_critical}")
        print(f"  Acknowledged: {services_ack}")

        # List unacknowledged problems
        host_problems = [h for h in hosts if h.problem and not h.acknowledged]
        service_problems = [s for s in services if s.problem and not s.acknowledged]

        if host_problems or service_problems:
            print(f"\n⚠️  Unacknowledged Problems:")

            if host_problems:
                print(f"\n  Hosts ({len(host_problems)}):")
                for host in host_problems:
                    print(f"    • {host.name}")

            if service_problems:
                print(f"\n  Services ({len(service_problems)}):")
                for service in service_problems:
                    print(f"    • {service.host_name}/{service.description}")
        else:
            print("\n✓ No unacknowledged problems")

if __name__ == "__main__":
    asyncio.run(status_report())
```

### Batch Operations

```python
import asyncio
from checkmk import Client

async def batch_acknowledge():
    """Acknowledge multiple services at once"""
    async with Client(...) as client:
        services = await client.get_services()

        # Find services matching criteria
        to_acknowledge = [
            s for s in services
            if s.problem
            and not s.acknowledged
            and "disk" in s.description.lower()
        ]

        print(f"Acknowledging {len(to_acknowledge)} disk services...")

        # Acknowledge all in parallel
        tasks = [
            service.acknowledge(
                comment="Disk space issue - adding more storage",
                sticky=True
            )
            for service in to_acknowledge
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        for service, result in zip(to_acknowledge, results):
            if isinstance(result, Exception):
                print(f"✗ {service.description}: {result}")
            else:
                print(f"✓ {service.description}")

if __name__ == "__main__":
    asyncio.run(batch_acknowledge())
```
