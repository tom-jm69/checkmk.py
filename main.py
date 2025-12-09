from checkmk import Client


async def main() -> None:
    async with Client(
        url="172.18.0.3",
        scheme="http",
        username="rest_api",
        secret="MkA3TEc$sF1OhPVt",
        site_name="cmk",
        port=5000,
        verify_ssl=False,
    ) as client:
        hosts = [host for host in await client.get_hosts()]
        # services = [service for service in await client.get_services()]
        for host in hosts:
            for service in await host.get_services():
                print(service.extensions.tags)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
