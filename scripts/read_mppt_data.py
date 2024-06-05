import asyncio
import argparse
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from common import get_buff, modbus_crc, s16
from dataclasses import dataclass
import textwrap


@dataclass
class RequestItem:
    dec_address: str
    description: str
    multiplier: int
    unit: str
    skip: bool = False


@dataclass
class ResponseItem:
    description: str
    value: float
    unit: str


class ModbusReader:
    def __init__(self, request_items: list[RequestItem], read_target, read_count):
        self.data = ""
        self.is_data_complete = False

        self.read_target = read_target
        self.read_count = read_count

        self.request_items = request_items
        self.response_data: list[ResponseItem] = []

    def run(self, args: argparse.Namespace):
        asyncio.run(self.main(args))

    def notification_handler(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        data = data.hex()

        if data and not self.is_data_complete:
            self.data += data
            crc = modbus_crc(self.data[:-4]) if len(self.data) > 4 else None
            length_match = (10 + (self.read_count * 4)) == len(self.data)

            if crc and self.data.endswith(crc) and length_match:
                self.is_data_complete = True

            print(f"[GATT Notification] CRC {crc} | {data} | completed: {self.is_data_complete}")

    def process_data(self):
        values = self.data[6:-4]
        print(f"data complete, parsing... {values}")

        split_values = textwrap.wrap(values, 4)

        for id, value in enumerate(split_values):
            item = self.request_items[id]

            if not item.skip:
                dec_value = s16(int(value, 16)) / item.multiplier
                self.response_data.append(ResponseItem(item.description, dec_value, item.unit))

    def cleanup(self):
        self.data = ""
        self.is_data_complete = False

    async def main(self, args: argparse.Namespace):
        print("starting scan...")

        device = await BleakScanner.find_device_by_address(args.address)

        if device is None:
            print(f"could not find device with address {args.address}")

        else:
            print("connecting to device...")

            async with BleakClient(device) as client:
                print("connected")

                await client.start_notify(args.notify_char, self.notification_handler)

                buff = get_buff(self.read_target, self.read_count)

                await client.write_gatt_char(args.write_char, buff)

                await asyncio.sleep(10)
                await client.stop_notify(args.notify_char)

            if not self.is_data_complete:
                print("received incomplete data !")

            else:
                self.process_data()

                if len(self.response_data) > 0:
                    print("parsed data")

                    for item in self.response_data:
                        print(f"{item.description} -> {item.value} {item.unit}")

            self.cleanup()

            print("done...")


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

    args = parser.parse_args()

    request_items = [
        RequestItem("0d12357", "Battery remaining capacity", 1, "%"),
        RequestItem("0d12358", "Battery voltage", 100, "V"),
        RequestItem("0d12359", "Battery current", 100, "A"),
        RequestItem("0d12360", "Battery power", 100, "W"),
        RequestItem("0d12361", "Battery power", 100, "W", skip=True),
        RequestItem("0d12362", "Load voltage", 100, "V"),
        RequestItem("0d12363", "Load current", 100, "A"),
        RequestItem("0d12364", "Load power", 100, "W"),
        RequestItem("0d12365", "Load power", 100, "W", skip=True),
        RequestItem("0d12366", "Solar voltage", 100, "V"),
        RequestItem("0d12367", "Solar current", 100, "A"),
    ]

    reader = ModbusReader(request_items=request_items, read_target="3045", read_count=len(request_items))
    reader.run(args)
