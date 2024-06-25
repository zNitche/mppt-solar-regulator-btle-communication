import json
import aioble
import asyncio


def load_config():
    with open("/config.json", "r") as file:
        config = json.loads(file.read())

    return config


async def scan_devices():
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            print(result, result.name(), result.rssi, result.services())


async def connect_to_device(address: str, connection_timeout=2000) -> aioble.central.DeviceConnection | None:
    connection = None
    device = aioble.Device(aioble.ADDR_PUBLIC, address)

    try:
        connection = await device.connect(timeout_ms=connection_timeout)
    except asyncio.TimeoutError:
        print(f"timeout while connecting to {address}")

    return connection
