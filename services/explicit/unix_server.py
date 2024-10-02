import asyncio
import logging
import os
import struct

from pathlib import Path

from minutia.common.explicit import unix_read, unix_packet
from . import explicit


logger = logging.getLogger(__name__)


# ====================================================================
# Server
# ====================================================================

async def init(path: str | Path, debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if os.path.exists(path):
        os.remove(path)
        logger.info("Removed file at %s", path)

    server = await asyncio.start_unix_server(_client_handler, path=path)
    async with server:
        logger.info("Server ready")
        logger.info("Listening at %s", path)
        await server.serve_forever()


async def _client_handler(reader, writer):
    logger.info("Client connected")
    while True:
        inp = await unix_read(reader)
        if not inp:
            logger.info("Client disconnected")
            break

        match inp:
            case 1, path:  # predict_image (with fs path)
                path_s = path.decode("utf-8")
                perc = explicit.predict_image(path_s)
                perc_b = struct.pack(">f", perc)
                out = unix_packet(1, perc_b)
                writer.write(out)
                await writer.drain()
                logger.debug("predict_image(%s) -> %s", path_s, perc)
            case 2, path:  # predict_video (with fs path)
                path_s = path.decode("utf-8")
                perc = explicit.predict_video(path_s)
                perc_b = struct.pack(">f", perc)
                out = unix_packet(2, perc_b)
                writer.write(out)
                await writer.drain()
                logger.debug("predict_video(%s) -> %s", path_s, perc)

    writer.close()
    await writer.wait_closed()
