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
import tempfile

from minutia import common, config
from minutia.http import fallback, hparser, utils

logger = logging.getLogger("libminutia")

try:
    from pymediainfo import MediaInfo  # type: ignore
except ImportError:
    _has_mediainfo = False
    logger.warning("[libminutia] audio: unavailable")
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

    with tempfile.NamedTemporaryFile() as fp:
        filesize = 0
        async for chunk in r.aiter_raw():
            filesize += len(chunk)
            if filesize >= config.max_filesize:
                return await fallback.handle(r)
            fp.write(chunk)

        fp.seek(0)
        title, duration, album, artist, date = get_mediainfo(fp.name)

    name = hparser.filename(r.headers)
    size = hparser.filesize(r.headers)
    mt = hparser.mimetype(r.headers)

    t = (f"{artist} - {title} ({duration}), {album}, {date}, {mt}, {name}"
         f", Size: {size}")
    t = t.replace("None - None ", "")  # No artist and no title
    t = t.replace("None - ", "")  # No artist
    t = t.replace(" - None", "")  # No title
    t = t.replace(" (None)", "")  # No duration
    t = t.replace(", None", "")  # Missing album and/or date
    t = t.replace("None, ", "")  # No name

    return {
        "@": "http:file:audio",
        "t": t,

        "album": album,
        "artist": artist,
        "date": date,
        "duration": duration,
        "explicit": utils.get_explicit(r),
        "filename": name,
        "mimetype": mt,
        "size": size,
        "title": title
    }


def get_mediainfo(path: str):
    title = None
    duration = None
    album = None
    performer = None
    date = None

    mediainfo = MediaInfo.parse(path)
    for track in mediainfo.tracks:
        if not title:
            title = track.title or track.movie_name or track.track_name
        if not album:
            album = track.album
        if not performer:
            performer = track.performer or track.album_performer
        if not date:
            date = track.recorded_date
        if not duration:
            try:
                duration = common.convert_time(track.duration)
            except TypeError:
                duration = None

    return title, duration, album, performer, date
