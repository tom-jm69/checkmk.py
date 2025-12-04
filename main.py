from checkmk import Client


async def main() -> None:
    client = Client(
        url="172.18.0.3",
        scheme="http",
        username="rest_api",
        secret="pQgh5x5mL*eKjVPA",
        site_name="cmk",
        port=5000,
        verify_ssl=False
    )
    try:
        hosts = await client.get_hosts()
        for host in hosts:
            await host.acknowledge("test")
        services = await client.get_services()
        for service in services:
            await service.acknowledge("test")
    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
