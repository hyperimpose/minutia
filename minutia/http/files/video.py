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

import logging
import mimetypes
import tempfile

from minutia import common, config
from minutia.http import fallback, hparser, utils

logger = logging.getLogger("minutia")

try:
    from pymediainfo import MediaInfo  # type: ignore
except ImportError:
    _has_mediainfo = False
    logger.warning("[minutia] video: unavailable")
else:
    _has_mediainfo = True


async def handle(r):
    if not _has_mediainfo:
        return await fallback.handle(r)

    try:
        length = int(r.headers.get("content-length", None))
    except TypeError:
        length = None

    if (not length) or (length > config.max_filesize):
        return await fallback.handle(r)

    name = hparser.filename(r.headers)
    size = hparser.filesize(r.headers)
    mt = hparser.mimetype(r.headers)

    # This is needed because the explicit service will use FFmpeg to extract
    # video frames for processing.
    # FFmpeg uses the filename to find the video format.
    ext = mimetypes.guess_extension(mt, strict=False) or ""

    with tempfile.NamedTemporaryFile(suffix=ext) as fp:
        filesize = 0
        async for chunk in r.aiter_raw():
            filesize += len(chunk)
            if filesize >= config.max_filesize:
                return await fallback.handle(r)
            fp.write(chunk)

        fp.seek(0)
        title, duration, width, height = get_mediainfo(fp.name)

        explicit = 0.0
        if ext:
            fp.seek(0)
            explicit = await utils.get_explicit(r, fp.name, duration=duration)

    duration = common.convert_time(duration)

    t = f"{title} ({duration}), {mt}, {name}, {width}x{height}, Size: {size}"
    t = t.replace("None ", "")  # No title
    t = t.replace("None, ", "")  # No name

    return {
        "@": "http:file:video",
        "t": t,

        "duration": duration,
        "explicit": explicit,
        "filename": name,
        "height": height,
        "mimetype": mt,
        "size": size,
        "title": title,
        "width": width
    }


def get_mediainfo(path: str):
    title = None
    duration = None
    width = None
    height = None

    mediainfo = MediaInfo.parse(path)
    for track in mediainfo.tracks:
        if not title:
            title = track.title or track.movie_name or track.track_name
        if not width:
            width = track.width
        if not height:
            height = track.height
        if not duration:
            try:
                duration = int(track.duration)
            except TypeError:
                duration = None

    return title, duration, width, height
