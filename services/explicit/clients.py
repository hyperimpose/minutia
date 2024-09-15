import asyncio
import logging
import struct

from . import unix_helpers


logger = logging.getLogger(__name__)


# NOTE: All client classes must at the very least implement the methods:
#       connect, predict_image, predict_video, close
#       Those methods must have the same signature across all implementations

# NOTE: Clients must always return a result. Even on errors.


class UnixClient:
    def __init__(self, path):
        self.path = path
        self.r = None
        self.w = None

    async def connect(self):
        try:
            self.r, self.w = await asyncio.open_unix_connection(self.path)
        except ConnectionRefusedError:
            logger.error("[minutia:explicit] Socket error", exc_info=True)

    async def predict_image(self, path: str) -> float:
        return await self._cmd_path(1, path)

    async def predict_video(self, path: str) -> float:
        return await self._cmd_path(2, path)

    async def _cmd_path(self, cmd: int, path: str) -> float:
        if not self.r or not self.w:
            logger.warning("[minutia:explicit] Not connected")
            return 0.0

        out = unix_helpers.packet(cmd, path.encode("utf-8"))
        try:
            self.w.write(out)
            await self.w.drain()
        except ConnectionResetError:
            logger.error("[minutia:explicit] Unix socket error", exc_info=True)
            # Try to reconnect to the socket so that maybe next time it works
            await self.connect()
            return 0.0

        inp = await unix_helpers.read(self.r)
        if not inp:
            logger.error("[minutia:explicit] Unable to read from socket")
            return 0.0

        match inp:
            case x, reply if x == cmd:
                return struct.unpack(">f", reply)[0]
            case other:
                logger.error("[minutia:explicit] Unexpected response: %s",
                             other,
                             stack_info=True)
                return 0.0

    async def close(self):
        self.w.close()
        await self.w.wait_closed()
