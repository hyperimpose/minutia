import asyncio


async def read(reader) -> tuple[int, bytes]:
    try:
        command_b = await reader.readexactly(1)  # 1 byte for the command
        command = int.from_bytes(command_b, "big")

        length_b = await reader.readexactly(2)  # 2 bytes for the data length
        length = int.from_bytes(length_b, "big")

        data = await reader.readexactly(length)
        assert len(data) == length
    except asyncio.IncompleteReadError:
        return None

    return command, data


def packet(command: int, data: bytes):
    command_b = command.to_bytes(1, "big")
    length_b = len(data).to_bytes(2, "big")
    return command_b + length_b + data
