from checkmk import Client


async def main() -> None:
    async with Client(
        url="172.20.0.3",
        scheme="http",
        username="itsmbot",
        secret="P3bFwvynwMWtMOUi",
        site_name="cmk",
        port=5000,
        verify_ssl=False,
    ) as client:
        for host in await client.get_hosts():
            print(host.groups)

        for host_group in await client.get_host_groups():
            print(host_group.name, host_group.num_hosts, host_group.worst_host_state)

        for service_group in await client.get_service_groups():
            print(service_group.name, service_group.num_services, service_group.worst_service_state)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
