# checkmk.py

A modern async API wrapper for the Checkmk API written in Python.

> **Disclaimer**
> checkmk.py is an independent, third-party REST wrapper for Checkmk®.
> It is **not** an official product of Checkmk or tribe29 GmbH, and it is
> neither affiliated with nor endorsed by them.
> All trademarks are the property of their respective owners.

## Features

- **Async/await support** - Built with asyncio for concurrent operations
- **Type hints** - Full type annotations for better IDE support
- **Pydantic models** - Structured data models with validation
- **Comprehensive API** - Access hosts, services, comments, acknowledgements
- **Error handling** - Rich exception hierarchy for better error handling
- **Automatic retries** - Built-in retry logic with exponential backoff

## Installing

**Python 3.11 or higher is required**

### Install from Git

You can install the latest version from the repository:

```bash
$ git clone https://github.com/tom-jm69/checkmk.py
$ cd checkmk.py
$ python3 -m pip install -U .
```

### Install with uv

To install using [uv](https://github.com/astral-sh/uv):

```bash
# Install latest from main branch
$ uv add "checkmk-py @ git+https://github.com/tom-jm69/checkmk.py"

# Install specific tag
$ uv add "checkmk-py @ git+https://github.com/tom-jm69/checkmk.py@0.1.0"
```

## Quick Example

```python
import asyncio
from checkmk import Client

async def main():
    async with Client(
        url="checkmk.example.com",
        site_name="mysite",
        username="automation",
        secret="your-api-secret",
        verify_ssl=True
    ) as client:
        # Get all hosts
        hosts = await client.get_hosts()
        for host in hosts:
            print(f"Host: {host.name}, State: {host.state}")

        # Get all services
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.description}, State: {service.state}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

Detailed documentation is available in the [docs](docs/) folder:

- **[Client](docs/client.md)** - Client initialization and configuration
- **[Host](docs/host.md)** - Working with hosts, properties, and methods
- **[Service](docs/service.md)** - Working with services, properties, and methods
- **[Error Handling](docs/errors.md)** - Exception hierarchy and error handling
- **[Examples](docs/examples.md)** - Practical examples for common use cases

## Quick Links

### Getting Started
- [Client Setup](docs/client.md#initialization)
- [Fetching Hosts](docs/host.md#getting-hosts)
- [Fetching Services](docs/service.md#getting-services)

### Common Tasks
- [Acknowledge Problems](docs/host.md#acknowledge)
- [Add Comments](docs/service.md#add_comment)
- [Check Host Services](docs/host.md#get_services)

### Error Handling
- [Exception Hierarchy](docs/errors.md#exception-hierarchy)
- [HTTP Errors](docs/errors.md#http-errors)
- [Handling Acknowledgement Errors](docs/errors.md#problem-acknowledgement-errors)

## Basic Usage

### Working with Hosts

```python
# Get all hosts
hosts = await client.get_hosts()

# Check host status
for host in hosts:
    if host.problem and not host.acknowledged:
        await host.acknowledge(comment="Working on it")

    # Get services for this host
    services = await host.get_services()
```

See [Host Documentation](docs/host.md) for more details.

### Working with Services

```python
# Get all services
services = await client.get_services()

# Check service status
for service in services:
    if service.state == ServiceStates.CRITICAL:
        await service.acknowledge(comment="Investigating")
```

See [Service Documentation](docs/service.md) for more details.

### Error Handling

```python
from checkmk import (
    ServiceNoProblemError,
    ServiceProblemAlreadyAcknowledgedError
)

try:
    await service.acknowledge(comment="Working on it")
except ServiceProblemAlreadyAcknowledgedError:
    print("Already acknowledged")
except ServiceNoProblemError:
    print("No problem to acknowledge")
```

See [Error Handling Documentation](docs/errors.md) for more details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
