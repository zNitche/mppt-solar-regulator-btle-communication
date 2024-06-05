from common import modbus_crc
import argparse


def main(args: argparse.Namespace):
    crc = modbus_crc(args.msg)
    print(crc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--msg",
        type=str,
    )

    args = parser.parse_args()
    main(args)
