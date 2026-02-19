from checkmk import Client


async def main() -> None:
    async with Client(
        url="172.18.0.4",
        scheme="http",
        username="rest_api",
        secret="^AJSdQMiEylFOSQ3",
        site_name="cmk",
        port=5000,
        verify_ssl=False,
    ) as client:
        for host in await client.get_hosts():
            print(host.ipv6)
            print(host.ipv4)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
