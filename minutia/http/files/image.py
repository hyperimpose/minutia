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
import struct
import tempfile

from minutia import config
from minutia.http import hparser, utils

import imagesize  # type: ignore

logger = logging.getLogger("minutia")

try:
    from PIL import (
        Image,
        ExifTags,
        UnidentifiedImageError
    )
except ImportError:
    _has_pillow = False
    logger.warning("[minutia] image: limited availability")
else:
    _has_pillow = True


async def handle(r):
    is_complete = True
    with tempfile.NamedTemporaryFile() as fp:
        filesize = 0
        async for chunk in r.aiter_raw():
            filesize += len(chunk)
            fp.write(chunk)
            if filesize >= config.max_filesize:
                is_complete = False
                break

        fp.seek(0)
        return await handle1(r, fp, is_complete)


async def handle1(r, fp, is_complete=False):
    mimetype = hparser.mimetype(r.headers)
    filename = hparser.filename(r.headers)
    filesize = hparser.filesize(r.headers)

    if is_complete:
        width, height, artist, title = info_pillow(fp)
        explicit = await utils.get_explicit(r, fp.name)
    else:
        width, height = info_imagesize(fp)
        explicit = await utils.get_explicit(r)
        artist = None
        title = None

    t = mimetype
    if title:
        t += f", {title}"
    if artist:
        t += f" by {artist}"
    if filename:
        t += f", {filename}"
    if width and height:
        t += f", {width}x{height}"
    if filesize:
        t += f", Size: {filesize}"

    return {
        "@": "http:file:image",
        "t": t,

        "artist": artist,
        "explicit": explicit,
        "filename": filename,
        "height": height,
        "mimetype": mimetype,
        "size": filesize,
        "title": title,
        "width": width
    }


def info_imagesize(fp):
    try:
        w, h = imagesize.get(fp.name)
        # Unsupported files return (-1, -1)
        # See: https://github.com/shibukawa/imagesize_py/issues/30
        if w > 0 and h > 0:
            return w, h
    except (ValueError, struct.error):
        pass

    return None, None


def info_pillow(fp):
    try:
        img = Image.open(fp)
        exif = img.getexif()

        width, height = img.size
        artist = exif.get(ExifTags.Base.Artist, "").strip() or None
        title = (
            exif.get(ExifTags.Base.ImageDescription, "")
            or exif.get(ExifTags.Base.UserComment, "")
            or exif.get(ExifTags.Base.PageName, "")
            or exif.get(ExifTags.Base.DocumentName, "")
        ).strip() or None

        return width, height, artist, title
    except (IOError, Image.DecompressionBombError, UnidentifiedImageError):
        # IOError is for when the image is truncated
        return None, None, None, None
