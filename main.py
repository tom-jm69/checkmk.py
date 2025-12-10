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
        hosts = [host for host in await client.get_hosts()]
        # services = [service for service in await client.get_services()]
        for host in hosts:
            vars = host.custom_variables
            if vars:
                print(vars.get("TAGS"))
            tags = host.tags
            if tags:
                print(tags.get("agent"))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
