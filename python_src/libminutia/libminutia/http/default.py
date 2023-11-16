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

from . import fallback, hparser, html, mediainfo, mupdf, png, utils

handler_d = {
    "application/xhtml+xml": html.handle,
    "text/html": html.handle,

    "audio/3gpp": mediainfo.audio,
    "audio/3gpp2": mediainfo.audio,
    "audio/aac": mediainfo.audio,
    "audio/flac": mediainfo.audio,
    "audio/midi": mediainfo.audio,
    "audio/x-midi": mediainfo.audio,
    "audio/mpeg": mediainfo.audio,
    "audio/ogg": mediainfo.audio,
    "application/ogg": mediainfo.audio,
    "audio/opus": mediainfo.audio,
    "audio/wav": mediainfo.audio,
    "audio/webm": mediainfo.audio,
    "audio/x-matroska": mediainfo.audio,

    "image/bmp": mediainfo.image,
    "image/gif": mediainfo.image,
    "image/jpeg": mediainfo.image,
    "image/tiff": mediainfo.image,
    "image/vnd.microsoft.icon": mediainfo.image,
    "image/webp": mediainfo.image,

    "video/3gpp": mediainfo.video,
    "video/3gpp2": mediainfo.video,
    "video/mp4": mediainfo.video,
    "video/mpeg": mediainfo.video,
    "video/ogg": mediainfo.video,
    "video/webm": mediainfo.video,
    "video/x-matroska": mediainfo.video,
    "video/x-msvideo": mediainfo.video,

    "application/pdf": mupdf.handle,
    "application/vnd.ms-xpsdocument": mupdf.handle,
    "application/oxps": mupdf.handle,
    "application/epub+zip": mupdf.handle,
    "application/x-mobipocket-ebook": mupdf.handle,
    "image/svg+xml": mupdf.handle,

    "image/png": png.handle,
}


async def get(link: str, headers={}):
    async with utils.client.stream(
            'GET', link, follow_redirects=True, headers=headers) as r:

        if r.status_code != 200:
            return False  # Must be False so we can retry with a web browser

        mimetype = hparser.mimetype(r.headers) or "application/octet-stream"

        handler = handler_d.get(mimetype, fallback.handle)
        content = await handler(link, r)

        if content:
            content.update({"_ttl": utils.cache(r.headers)})
            return "ok", content
        else:
            return False
