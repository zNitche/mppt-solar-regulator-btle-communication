import aioble
import bluetooth
import common, utils


async def mainloop():
    print("loading config...")
    config = utils.load_config()

    # print("scanning devices...")
    # await utils.scan_devices()

    print("connecting to target...")
    connection = await utils.connect_to_device(config.get("MAC_ADDRESS"))

    if connection:
        print(f"connected to {connection.device}")

        async with connection:
            print("connection...")

            # services = []
            #
            # async for service in connection.services():
            #     print(service, service.uuid)
            #     services.append(service)
            #
            # for service in services:
            #     async for char in service.characteristics():
            #         print(char)

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
