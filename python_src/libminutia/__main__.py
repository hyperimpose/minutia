# --------------------------------------------------------------------
# Copyright (C) 2023 hyperimpose.org
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
import os
import traceback

import libminutia


# ====================================================================
# Erlang
# ====================================================================

# Erlang Port Settings
FD_IN = 0
FD_OUT = 1


# Readers ============================================================

async def read_packet(loop) -> bytes:
    return await loop.run_in_executor(None, _read_packet)


def _read_packet() -> bytes | None:
    length_b = os.read(0, 2)
    if len(length_b) != 2:  # We configure the erlang port with {packet, 2}
        return None  # The port closed

    length = int.from_bytes(length_b, "big")

    packet = os.read(FD_IN, length)
    assert len(packet) == length

    return packet


# Writers ============================================================

def write_data(packet: bytes):
    packet_len = len(packet).to_bytes(2, "big")
    os.write(FD_OUT, packet_len)
    os.write(FD_OUT, packet)


def send(term):
    write_data(bencode(term))


def log(level, term):
    send(("log", level, term))


# Helpers ============================================================

def bencode(term):
    """
    Simple recursive bencode encoder.

    - Because the data in libminutia are not deeply nested, it is unlikely that
      we will hit the recursion limit.
    - Booleans are converted to the strings 'true' and 'false'.
    - None is converted to the empty string.
    """
    if term is False:
        return b"5:false"
    if term is True:
        return b"4:true"
    if term is None:
        return b"0:"
    if isinstance(term, int):
        return b"i" + str(term).encode() + b"e"
    if isinstance(term, str):
        return bencode(term.encode())
    if isinstance(term, bytes):
        return str(len(term)).encode() + b":" + term
    if isinstance(term, list) or isinstance(term, tuple):
        return b"l" + b"".join([bencode(x) for x in term]) + b"e"
    if isinstance(term, dict):  # in Python 3.6+ dicts are ordered
        acc = b"d"
        for k, v in term.items():
            if not isinstance(k, str) and not isinstance(k, bytes):
                raise ValueError("Dictionary keys must be of type str or bytes")
            acc += bencode(k)
            acc += bencode(v)
        acc += b"e"
        return acc


# Commands ===========================================================

async def set_http_useragent(ua: str):
    libminutia.set_http_useragent(ua)
    log("debug", f"http_useragent set to {ua}")


async def set_lang(lang: str):
    libminutia.set_lang(lang)
    log("debug", f"lang set to {lang}")


async def set_max_filesize(i: int):
    libminutia.set_max_filesize(i)
    log("debug", f"max_filesize set to {i}")


async def set_max_htmlsize(i: int):
    libminutia.set_max_htmlsize(i)
    log("debug", f"max_htmlsize set to {i}")


async def http_get(link, lang):
    """
    Retrieve information for HTTP links.

    It sends back an dictionary that will always contain the keys:
    @     : str   : Indicates what other keys exist in the dictionary.
          : False : We were unable to extract any info.
    t     : str   : A title that describes the linked resource.
    _link : str   : The link argument given. Used for async keying.
    _lang : str   : The language argument given. Used for async keying.
    """
    match await libminutia.http.get(link, lang=lang):
        case "ok", payload:
            # Insert metadata. These are needed by the Erlang side for keying.
            payload.update({
                "_link": link,
                "_lang": lang
            })
            send(("http", payload))
        case False:  # Unable to get any information for this link
            payload = {
                "@": "false",
                "t": "",
                "_link": link,
                "_lang": lang
            }
            send(("http", payload))
        case "error", msg, exception:
            # We must always send a reply to the Erlang side, because otherwise
            # the link stays in the queue forever.
            payload = {
                "@": "error",
                "t": msg,
                "_link": link,
                "_lang": lang
            }
            send(("http", payload))
            if msg:
                log("debug", f"{link} - {exception} \n\n")
            else:  # No msg means the error is unexpected
                log("error", (f":( libminutia crashed @ {link} -> {exception}"
                              f"\n\n{traceback.format_exc()}"))


async def unknown_command(command, *args):
    log("error", f"Unknown command: {command} args: {args}")


# Dispatcher =========================================================

FUN_D = {
    256: set_http_useragent,
    255: set_lang,
    254: set_max_filesize,
    253: set_max_htmlsize,

    1: http_get
}


async def dispatch(packet: bytes):
    try:
        fid, args = parse_command(packet)
        fn = FUN_D.get(fid, lambda x: unknown_command(fid, x))
        await fn(*args)  # type: ignore
    except Exception as e:
        log("emergency", (f":( libminutia crashed -> {e}"
                          f"\n\n{traceback.format_exc()}"))


def parse_command(cmd):
    """
    The first byte points to the handler function (upto 256 functions).
    The rest of the bytes are a NUL delimited string with arguments
    for the function.
    By convention the first argument refers to the caller on the erlang side
    and must be included in the response.
    """
    fid = cmd[0]
    args = cmd[1:].split(b"\x00")
    args = [x.decode("utf-8") for x in args]
    return fid, args


# ====================================================================
# Main
# ====================================================================

async def main():
    await libminutia.init()

    loop = asyncio.get_running_loop()

    async with asyncio.TaskGroup() as tg:
        while packet := await read_packet(loop):
            tg.create_task(dispatch(packet))

    await libminutia.terminate()

asyncio.run(main())
