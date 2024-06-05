import asyncio
import argparse
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from common import get_buff, modbus_crc


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    data = data.hex()

    if data:
        response_crc_checksum = data[-4:]
        computed_crc_checksum = modbus_crc(data[:-4])

        print(f"is crc correct: {response_crc_checksum == computed_crc_checksum}")

    print(f"[Notification] {characteristic.description}: {data}")


async def main(args: argparse.Namespace):
    print("starting scan...")

    device = await BleakScanner.find_device_by_address(args.address)

    if device is None:
        print(f"could not find device with address {args.address}")

    else:
        print("connecting to device...")

        async with BleakClient(device) as client:
            print("connected")

            print(f"notify char = {args.notify_char}")
            print(f"write char = {args.write_char}")

            await client.start_notify(args.notify_char, notification_handler)

            read_target = args.read_target
            read_count = args.targets_to_read

            print(f"read target = {read_target}")
            print(f"targets to read = {read_count}")

            buff = get_buff(read_target, read_count)

            print(f"target buff = {buff}")

            await client.write_gatt_char(args.write_char, buff)

            await asyncio.sleep(10.0)
            await client.stop_notify(args.notify_char)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--address",
        type=str,
        help="address of target bluetooth device",
    )

    parser.add_argument(
        "--write_char",
        type=str,
        help="address of characteristic to write",
    )

    parser.add_argument(
        "--notify_char",
        type=str,
        help="address of notify characteristic",
    )

    parser.add_argument(
        "--read_target",
        type=str,
        help="hex data address to read",
    )

    parser.add_argument(
        "--targets_to_read",
        type=int,
        default=1,
        required=False,
        help="count of addresses to read",
    )

    args = parser.parse_args()

    asyncio.run(main(args))
