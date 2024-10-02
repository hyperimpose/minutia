# --------------------------------------------------------------------
# Copyright (C) 2024 hyperimpose.org
#
# This file is part of minutia.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

import asyncio
import logging
import struct


logger = logging.getLogger(__name__)


# ====================================================================
# Protocols / Clients
# ====================================================================

# NOTE: All client classes must at the very least implement the methods:
#       connect, predict_image, predict_video, close
#       Those methods must have the same signature across all implementations

# NOTE: Clients must always return a result. Even on errors.


# Unix sockets -------------------------------------------------------

async def unix_read(reader) -> tuple[int, bytes]:
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


def unix_packet(command: int, data: bytes):
    command_b = command.to_bytes(1, "big")
    length_b = len(data).to_bytes(2, "big")
    return command_b + length_b + data


class UnixClient:
    def __init__(self, path):
        self.path = path
        self.r = None
        self.w = None
        self.lock = asyncio.Lock()

    async def connect(self):
        try:
            self.r, self.w = await asyncio.open_unix_connection(self.path)
        except ConnectionRefusedError:
            logger.error("[minutia:explicit] Socket error", exc_info=True)

    async def predict_image(self, path: str) -> float:
        async with self.lock:
            return await self._cmd_path(1, path)

    async def predict_video(self, path: str) -> float:
        async with self.lock:
            return await self._cmd_path(2, path)

    async def _cmd_path(self, cmd: int, path: str) -> float:
        if not self.r or not self.w:
            logger.warning("[minutia:explicit] Not connected")
            return 0.0

        out = unix_packet(cmd, path.encode("utf-8"))
        try:
            self.w.write(out)
            await self.w.drain()
        except ConnectionResetError:
            logger.error("[minutia:explicit] Unix socket error", exc_info=True)
            # Try to reconnect to the socket so that maybe next time it works
            await self.connect()
            return 0.0

        inp = await unix_read(self.r)
        if not inp:
            logger.error("[minutia:explicit] Unable to read from socket")
            return 0.0

        match inp:
            case x, reply if x == cmd:
                return struct.unpack(">f", reply)[0]
            case other:
                logger.error("[minutia:explicit] Unexpected response %s"
                             " for file %s using command %s",
                             other, path, cmd,
                             stack_info=True)
                return 0.0

    async def close(self):
        self.w.close()
        await self.w.wait_closed()


# ====================================================================
# API
# ====================================================================

client: None | UnixClient = None  # Externally initialized


async def predict_image(inpath: str) -> float:
    if not client:
        return 0.0

    return await client.predict_image(inpath)


async def predict_video(inpath: str, duration=0) -> float:
    if not client:
        return 0.0

    return await client.predict_video(inpath)
