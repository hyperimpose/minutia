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

import tempfile

from pymediainfo import MediaInfo  # type: ignore

from libminutia import config
from libminutia.common import convert_size, convert_time
from libminutia.http import fallback


async def audio(url, r):
    match await _handle(url, r):
        case "error", "too_long":
            return await fallback.handle(url, r)
        case "ok", i:
            return audio1(i)


def audio1(i):
    album = i["audio"]["album"]
    artist = i["audio"]["artist"]
    date = i["audio"]["date"]
    duration = i["audio"]["duration"]
    ct = i["content_type"]
    size = i["size"]
    title = i["audio"]["title"]

    t = f"{artist} - {title} ({duration}), {album}, {date}, {ct}, Size: {size}"
    t = t.replace("None - None ", "")  # No artist and no title
    t = t.replace("None - ", "")  # No artist
    t = t.replace(" - None", "")  # No title
    t = t.replace(" (None)", "")  # No duration
    t = t.replace(", None", "")  # Missing album and/or date
    # mimetype and size will always be available

    return {
        "@": "http:mediainfo:audio",
        "t": t,

        "artist": artist,
        "title": title,
        "album": album,
        "date": date,
        "duration": duration,
        "format": i["audio"]["format"],

        "size": size,
        "content_type": ct,
        "explicit": i["explicit"],
    }


async def image(url, r):
    match await _handle(url, r):
        case "error", "too_long":
            return await fallback.handle(url, r)
        case "ok", i:
            return image1(i)


def image1(i):
    title = i["image"]["title"]
    width = i["image"]["width"]
    height = i["image"]["height"]
    size = i["size"]
    ct = i["content_type"]

    t = f"{title}, {ct}, {width}x{height}, Size: {size}"
    t = t.replace("None, ", "")  # No title

    return {
        "@": "http:mediainfo:image",
        "t": t,

        "title": title,
        "width": width,
        "height": height,
        "format": i["image"]["format"],

        "size": size,
        "content_type": ct,
        "explicit": i["explicit"]
    }


async def video(url, r):
    match await _handle(url, r):
        case "error", "too_long":
            return await fallback.handle(url, r)
        case "ok", i:
            return video1(i)


def video1(i):
    title = i["video"]["title"]
    width = i["video"]["width"]
    height = i["video"]["height"]
    duration = i["video"]["duration"]
    size = i["size"]
    content_type = i["content_type"]
    explicit = i["explicit"]

    t = f"{title} ({duration}), {content_type}, {width}x{height}, Size: {size}"
    t = t.replace("None ", "")  # No title

    return {
        "@": "http:mediainfo:video",
        "t": t,

        "title": title,
        "width": width,
        "height": height,
        "duration": duration,
        "format": i["video"]["format"],

        "size": size,
        "content_type": content_type,
        "explicit": explicit,
    }


async def _handle(url, r):
    content_type = r.headers.get("content-type")
    explicit = r.headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA"

    try:
        length = int(r.headers.get("content-length", None))
    except TypeError:
        length = None

    if (not length) or (length > config.max_filesize):
        return "error", "too_long"

    with tempfile.NamedTemporaryFile() as fp:
        filesize = 0
        async for chunk in r.aiter_raw():
            filesize += len(chunk)
            if filesize >= config.max_filesize:
                return "error", "too_long"
            fp.write(chunk)

        fp.seek(0)

        info = get_mediainfo(fp.name)
        info.update({
            "size": convert_size(length),
            "content_type": content_type,
            "explicit": explicit
        })

        return "ok", info


def get_mediainfo(path):
    # General
    title = None
    format = None
    # Music / Video
    duration = None
    # Music
    album = None
    performer = None
    date = None
    # Video / Image
    width = None
    height = None

    mediainfo = MediaInfo.parse(path)
    for track in mediainfo.tracks:
        if not title:
            title = track.title or track.movie_name or track.track_name
        if not format:
            format = track.format
        if not album:
            album = track.album
        if not performer:
            performer = track.performer or track.album_performer
        if not date:
            date = track.recorded_date
        if not width:
            width = track.width
        if not height:
            height = track.height
        if not duration:
            try:
                duration = convert_time(track.duration)
            except TypeError:
                duration = None

    return {
        "audio": {
            "format": format,
            "title": title,
            "duration": duration,
            "album": album,
            "artist": performer,
            "date": date
        },
        "image": {
            "format": format,
            "title": title,
            "width": width,
            "height": height
        },
        "video": {
            "format": format,
            "title": title,
            "duration": duration,
            "width": width,
            "height": height
        }
    }
