import json
import asyncio
import aioble
from aioble.central import DeviceConnection


def load_config():
    with open("/config.json", "r") as file:
        config = json.loads(file.read())

    return config


async def scan_devices():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print(result, result.name(), result.rssi, result.services())


async def connect_to_device(address: str) -> DeviceConnection | None:
    connection = None
    device = aioble.Device(aioble.ADDR_PUBLIC, address)

    try:
        connection = await device.connect(timeout_ms=2000)
    except asyncio.TimeoutError:
        print(f"timeout while connecting to {address}")

    return connection


async def mainloop():
    print("loading config...")
    config = load_config()

    # print("scanning devices...")
    # await scan_devices()

    print("connecting to target...")
    connection = await connect_to_device(config.get("MAC_ADDRESS"))

    if connection:
        print(f"connected to {connection.device}")

        async with connection:
            print("connection...")

            services = []

            async for service in connection.services():
                print(service, service.uuid)
                services.append(service)

            for service in services:
                async for char in service.characteristics():
                    print(char)

    print("done")


def main():
    asyncio.run(mainloop())


if __name__ == '__main__':
    main()
