# --------------------------------------------------------------------
# Copyright (C) 2023-2024 hyperimpose.org
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
import contextlib
import io
import logging
import traceback

from erlang import log, read_packet, send, ErlangLogHandler


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[ErlangLogHandler()]
)


import minutia  # noqa


# ====================================================================
# Minutia
# ====================================================================

# Commands ===========================================================

async def set_http_useragent(ua: str):
    minutia.set_http_useragent(ua)
    log("debug", f"http_useragent set to {ua}")


async def set_lang(lang: str):
    minutia.set_lang(lang)
    log("debug", f"lang set to {lang}")


async def set_max_filesize(i: str):
    minutia.set_max_filesize(int(i))
    log("debug", f"max_filesize set to {i}")


async def set_max_htmlsize(i: str):
    minutia.set_max_htmlsize(int(i))
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
    match await minutia.http.get(link, lang=lang):
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
                tb = "".join(traceback.format_exception(exception))
                log("error", (f":( minutia crashed @ {link} -> {exception}"
                              f"\n\n{tb}"))


async def unknown_command(command, *args):
    log("error", f"Unknown command: {command} args: {args}")


# Dispatcher =========================================================

FUN_D = {
    255: set_http_useragent,
    254: set_lang,
    253: set_max_filesize,
    252: set_max_htmlsize,

    1: http_get
}


async def dispatch(packet: bytes):
    try:
        fid, args = parse_command(packet)
        fn = FUN_D.get(fid, lambda x: unknown_command(fid, x))
        with (contextlib.redirect_stdout(io.StringIO()) as out,
              contextlib.redirect_stderr(io.StringIO()) as err):
            await fn(*args)  # type: ignore

            outv = out.getvalue()
            if outv:
                log("info", outv)

            errv = err.getvalue()
            if errv:
                log("notice", errv)
    except Exception as e:
        log("emergency", (f":( minutia crashed -> {e}"
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
    await minutia.init()

    loop = asyncio.get_running_loop()

    async with asyncio.TaskGroup() as tg:
        while packet := await read_packet(loop):
            tg.create_task(dispatch(packet))

    await minutia.terminate()

asyncio.run(main())
