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

from . import fallback, files, hparser, html, utils

handler_d = {
    "application/xhtml+xml": html.handle,
    "text/html": html.handle,

    "audio/3gpp": files.handle_audio,
    "audio/3gpp2": files.handle_audio,
    "audio/aac": files.handle_audio,
    "audio/flac": files.handle_audio,
    "audio/midi": files.handle_audio,
    "audio/x-midi": files.handle_audio,
    "audio/mpeg": files.handle_audio,
    "audio/ogg": files.handle_audio,
    "application/ogg": files.handle_audio,
    "audio/opus": files.handle_audio,
    "audio/wav": files.handle_audio,
    "audio/webm": files.handle_audio,
    "audio/x-matroska": files.handle_audio,

    "image/gif": files.handle_image,
    "image/x-icns": files.handle_image,
    "image/sgi": files.handle_image,
    "image/webp": files.handle_image,
    "image/vnd-ms.dds": files.handle_image,
    "image/vnd.fpx": files.handle_image,
    "image/vnd.adobe.photoshop": files.handle_image,
    # BMP
    "image/bmp": files.handle_image,
    "image/x-bmp": files.handle_image,
    # EPS
    "application/eps": files.handle_image,
    "application/x-eps": files.handle_image,
    "image/eps": files.handle_image,
    "image/x-eps": files.handle_image,
    # ICO
    "image/x-icon": files.handle_image,
    "image/ico": files.handle_image,
    "image/vnd.microsoft.icon": files.handle_image,
    # JPEG / JPEG 2000
    "image/jpeg": files.handle_image,
    "image/jp2": files.handle_image,
    "image/jpx": files.handle_image,
    "image/jpm": files.handle_image,
    # FITS
    "image/fits": files.handle_image,
    "application/fits": files.handle_image,
    # Netpbm / PPM
    "image/x-portable-bitmap": files.handle_image,
    "image/x-portable-graymap": files.handle_image,
    "image/x-portable-pixmap": files.handle_image,
    "image/x-portable-anymap": files.handle_image,
    # PCX
    "image/vnd.zbrush.pcx": files.handle_image,
    "image/x-pcx": files.handle_image,
    # PNG / APNG
    "image/png": files.handle_image,
    "image/vnd.mozilla.apng": files.handle_image,
    "image/apng": files.handle_image,
    # TGA
    "image/x-targa": files.handle_image,
    "image/x-tga": files.handle_image,
    # TIFF
    "image/tiff": files.handle_image,
    "image/tiff-fx": files.handle_image,
    # X BitMap / XBM
    "image/x-xbitmap": files.handle_image,
    "image/x-xbm": files.handle_image,
    # X PixMap / XPM
    "image/x-xpixmap": files.handle_image,

    "video/3gpp": files.handle_video,
    "video/3gpp2": files.handle_video,
    "video/mp4": files.handle_video,
    "video/mpeg": files.handle_video,
    "video/ogg": files.handle_video,
    "video/webm": files.handle_video,
    "video/x-matroska": files.handle_video,
    "video/x-msvideo": files.handle_video,

    "application/pdf": files.handle_mupdf,
    "application/vnd.ms-xpsdocument": files.handle_mupdf,
    "application/oxps": files.handle_mupdf,
    "application/epub+zip": files.handle_mupdf,
    "application/x-mobipocket-ebook": files.handle_mupdf,
    "image/svg+xml": files.handle_mupdf
}


async def get(link: str, headers={}):
    async with utils.client.stream(
            'GET', link, follow_redirects=True, headers=headers) as r:

        if r.status_code != 200:
            return False

        mimetype = hparser.mimetype(r.headers) or "application/octet-stream"

        handler = handler_d.get(mimetype, fallback.handle)
        content = await handler(r)

        if content:
            content.update({"_ttl": utils.cache(r.headers)})
            return "ok", content
        else:
            return False
