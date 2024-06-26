import aioble
import bluetooth
import common
import asyncio


async def connect_to_device(device_address):
    connection = None
    device = aioble.Device(aioble.ADDR_PUBLIC, device_address)

    try:
        connection = await device.connect(timeout_ms=2000)
    except asyncio.TimeoutError:
        print(f"timeout while connecting to {device_address}")

    return connection


async def bare_mppt_reading(config: dict[str, str]):
    print("connecting to target...")
    connection = await connect_to_device(config.get("MAC_ADDRESS"))

    if connection:
        print(f"connected to {connection.device}")

        async with connection:
            print("connection...")

            service_uuid = bluetooth.UUID(0xff00)
            write_char_uuid = bluetooth.UUID(0xff02)
            notify_char_uuid = bluetooth.UUID(0xff01)

            data_service: aioble.Service = await connection.service(service_uuid)

            write_char: aioble.Characteristic = await data_service.characteristic(write_char_uuid)
            notify_char: aioble.Characteristic = await data_service.characteristic(notify_char_uuid)

            print("subscribing for notifications")
            await notify_char.subscribe(notify=True)

            read_count = 5
            write_buff = common.get_buff("304E", count=read_count)

            print(f"writing buff {write_buff}")
            await write_char.write(write_buff)

            print("waiting for response")

            data_str = ""

            while True:
                data = await notify_char.notified(timeout_ms=5000)
                data = data.hex()

                if data:
                    data_str += data
                    crc = common.modbus_crc(data_str[:-4]) if len(data_str) > 4 else None
                    length_match = (10 + (read_count * 4)) == len(data_str)

                    if crc and data_str.endswith(crc) and length_match:
                        break

                    print(f"[Notification] CRC {crc} | {data}")

            print(data_str)

    print("done")
