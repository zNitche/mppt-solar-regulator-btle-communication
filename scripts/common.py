def modbus_crc(input_msg: str) -> str:
    msg = bytes.fromhex(input_msg)
    crc = 0xFFFF

    for n in range(len(msg)):
        crc ^= msg[n]

        for _ in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001

            else:
                crc >>= 1

    output = crc.to_bytes(2, byteorder="little").hex()

    return output


def get_buff(address: str, count: int = 1) -> bytes:
    # 1 device id
    # 2 instruction
    # 3 address to read
    # 4 number of addresses to reed
    buff = ["01", "04", address, format(count, "04x")]

    crc = modbus_crc("".join(buff))
    buff.append(crc.upper())

    return bytes.fromhex("".join(buff))


def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)
