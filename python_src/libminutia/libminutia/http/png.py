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

from libminutia.common import convert_size


SIZE = 26  # Min required size in bytes


async def handle(_url, r):
    data = b""
    async for chunk in r.aiter_raw(chunk_size=SIZE):
        data += chunk
        if len(data) >= SIZE:
            break

    w, h = parse_png(data)

    if w and h:
        t = f"image/png, {w}x{h}"
    else:
        t = "image/png"

    length = r.headers.get("content-length", None)
    size = None
    if length is not None:
        size = convert_size(length)
        t += f", Size: {convert_size(int(length))}"

    return {
        "@": "http:png",
        "t": t,

        "width": w,
        "height": h,

        "explicit": r.headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA",
        "size": size
    }


def parse_png(data):
    if data[1:4] != b"PNG" or data[12:16] != b"IHDR":
        return None, None

    w = int.from_bytes(data[16:20], "big")
    h = int.from_bytes(data[20:24], "big")

    return w, h
