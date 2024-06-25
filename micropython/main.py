import asyncio
import utils
from dataclasses import RequestItem
from mppt_reader import MpptReader


async def main():
    read_target_address = "3045"
    request_items = [
        RequestItem("0d12357", "Battery remaining capacity", 1, "%"),
        RequestItem("0d12358", "Battery voltage", 100, "V"),
        RequestItem("0d12359", "Battery current", 100, "A"),
        RequestItem("0d12360", "Battery power", 100, "W"),
        RequestItem("0d12361", "Battery power", 100, "W"),
        RequestItem("0d12362", "Load voltage", 100, "V"),
        RequestItem("0d12363", "Load current", 100, "A"),
        RequestItem("0d12364", "Load power", 100, "W"),
        RequestItem("0d12365", "Load power", 100, "W"),
        RequestItem("0d12366", "Solar voltage", 100, "V"),
        RequestItem("0d12367", "Solar current", 100, "A"),
    ]

    print("loading config...")
    config = utils.load_config()
    device_address = config.get("MAC_ADDRESS")

    reader = MpptReader(device_address=device_address,
                        service_uuid=0xff00,
                        write_char_uuid=0xff02,
                        notify_char_uuid=0xff01,
                        logging=True)

    data = await reader.read(request_items, read_target_address)

    if len(data) > 0:
        print("parsed data")

        for item in data:
            print(f"{item.description} -> {item.value} {item.unit}")


if __name__ == '__main__':
    asyncio.run(main())
