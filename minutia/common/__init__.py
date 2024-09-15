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

import math
import unicodedata

from . import explicit


def cleanup(s: str):
    s = " ".join(s.split())
    s = "".join(c for c in s if unicodedata.category(c)[0] != "C")
    s = "".join(" " if unicodedata.category(c)[0] == "Z" else c for c in s)
    return s


size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def convert_size(size_bytes):
    s = int(size_bytes)
    if s == 0:
        return "0 B"

    i = int(math.floor(math.log(s, 1024)))
    p = math.pow(1024, i)
    s = round(s / p, 2)

    return f"{s} {size_unit[i]}"


def convert_time(time_ms):
    ms = int(time_ms)
    s = int((ms / 1000) % 60)
    m = int((ms / (1000 * 60)) % 60)
    h = int((ms / (1000 * 60 * 60)) % 24)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


async def image_explicit_score(path: str) -> float:
    return await explicit.predict_image(path)


async def video_explicit_score(path: str, duration=0) -> float:
    return await explicit.predict_video(path, duration=duration)
