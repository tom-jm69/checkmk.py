from checkmk import Client


async def main() -> None:
    client = Client(url="172.18.0.3", verify_ssl=False, username="rest_api", secret="pQgh5x5mL*eKjVPA", site_name="cmk")
    services = await client.get_services()
    for service in services:



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


