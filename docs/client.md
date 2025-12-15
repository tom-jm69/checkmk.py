# Client

The `Client` is the main entry point for interacting with the Checkmk API.

## Initialization

```python
from checkmk import Client

async with Client(
    url="checkmk.example.com",      # Checkmk server hostname or IP
    site_name="mysite",               # Site name
    username="automation",             # Username for authentication
    secret="your-api-secret",         # Password or API secret
    scheme="https",                   # Connection scheme (default: "https")
    port=443,                         # Server port (default: 443)
    verify_ssl=True,                  # Verify SSL certificates (default: True)
    timeout=30,                       # Request timeout in seconds (default: 30)
    retries=5,                        # Number of retries (default: 5)
    api_version="1.0"                 # API version (default: "1.0")
) as client:
    # Your code here
    pass
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | Required | Checkmk server hostname or IP (without scheme) |
| `site_name` | `str` | Required | Checkmk site name |
| `username` | `str` | Required | Username for authentication |
| `secret` | `str` | Required | Password or API secret |
| `scheme` | `str` | `"https"` | Connection scheme (`http` or `https`) |
| `port` | `int` | `443` | Server port |
| `verify_ssl` | `bool` | `True` | Verify SSL certificates |
| `timeout` | `int` | `30` | Request timeout in seconds |
| `retries` | `int` | `5` | Number of retry attempts |
| `api_version` | `str` | `"1.0"` | Checkmk REST API version |

## Methods

### get_hosts()

Fetch all hosts from the Checkmk API.

```python
hosts = await client.get_hosts()
```

**Returns:** `List[Host]`

**Raises:**
- `HostFetchError` - Failed to fetch hosts
- `HostParseError` - Failed to parse host data

### get_services()

Fetch all services from the Checkmk API.

```python
services = await client.get_services()
```

**Returns:** `List[Service]`

**Raises:**
- `ServiceFetchError` - Failed to fetch services
- `ServiceParseError` - Failed to parse service data

### close()

Close the underlying HTTP session.

```python
await client.close()
```

**Note:** When using the async context manager (`async with`), this is called automatically.

## HTTP Client Features

The underlying HTTP client includes:

- **Automatic retry with exponential backoff** - Retries failed requests with increasing delays
- **Rate limit handling** - Automatically handles 429 responses with `Retry-After` headers
- **Server error retry** - Retries on 500, 502, 503, 504 errors
- **Custom timeouts** - Configurable request timeouts
- **SSL verification** - Optional SSL certificate verification

## Example Usage

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
        print(f"Found {len(hosts)} hosts")

        # Get all services
        services = await client.get_services()
        print(f"Found {len(services)} services")

if __name__ == "__main__":
    asyncio.run(main())
```

## Using with HTTP (Development)

For development or testing with HTTP:

```python
async with Client(
    url="localhost",
    site_name="cmk",
    username="automation",
    secret="your-secret",
    scheme="http",
    port=5000,
    verify_ssl=False
) as client:
    hosts = await client.get_hosts()
```
