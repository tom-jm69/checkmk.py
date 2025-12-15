from checkmk import Client


async def main() -> None:
    async with Client(
        url="172.18.0.2",
        scheme="http",
        username="rest_api",
        secret="MkA3TEc$sF1OhPVt",
        site_name="cmk",
        port=5000,
        verify_ssl=False,
    ) as client:
        for host in await client.get_hosts():
            print(host)
            for service in await host.get_services():
                print(service)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
