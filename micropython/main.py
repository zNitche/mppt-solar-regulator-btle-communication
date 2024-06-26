import asyncio
import json
from mppt_reader import MpptReader, RequestItem


def load_config():
    with open("/config.json", "r") as file:
        config = json.loads(file.read())

    return config


async def main():
    request_items = [
        RequestItem("12357", "Battery remaining capacity", 1, "%"),
        RequestItem("12358", "Battery voltage", 100, "V"),
        RequestItem("12359", "Battery current", 100, "A"),
        RequestItem("12360", "Battery power", 100, "W"),
        RequestItem("12361", "Battery power", 100, "W"),
        RequestItem("12362", "Load voltage", 100, "V"),
        RequestItem("12363", "Load current", 100, "A"),
        RequestItem("12364", "Load power", 100, "W"),
        RequestItem("12365", "Load power", 100, "W"),
        RequestItem("12366", "Solar voltage", 100, "V"),
        RequestItem("12367", "Solar current", 100, "A"),
    ]

    print("loading config...")
    config = load_config()
    device_address = config.get("MAC_ADDRESS")

    reader = MpptReader(device_address=device_address,
                        service_uuid=0xff00,
                        write_char_uuid=0xff02,
                        notify_char_uuid=0xff01,
                        logging=True)

    data = await reader.read(request_items)

    if len(data) > 0:
        print("parsed data")

        for item in data:
            print(f"{item.description} -> {item.value} {item.unit}")


if __name__ == '__main__':
    asyncio.run(main())
