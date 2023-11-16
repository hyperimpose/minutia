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

import fitz  # type: ignore

from libminutia import config
from libminutia.common import convert_size
from libminutia.http import fallback


MIME_TO_TYPE = {
    "application/pdf": "pdf",
    "application/vnd.ms-xpsdocument": "xps",
    "application/oxps": "oxps",
    "application/epub+zip": "epub",
    "application/x-mobipocket-ebook": "mobi",
    "image/svg+xml": "svg"
}


async def handle(url, r):
    length = r.headers.get("content-length", None)
    if not length:
        return await fallback.handle(url, r)

    try:
        length = int(length)
    except ValueError:
        return await fallback.handle(url, r)

    if length > config.max_filesize:
        return await fallback.handle(url, r)

    content_type = r.headers.get("content-type", None)
    if not content_type:
        return await fallback.handle(url, r)

    filetype = MIME_TO_TYPE[content_type]

    with tempfile.NamedTemporaryFile() as fp:
        filesize = 0
        async for chunk in r.aiter_raw():
            filesize += len(chunk)
            if filesize >= config.max_filesize:
                return await fallback.handle(url, r)
            fp.write(chunk)

        fp.seek(0)

        with fitz.open(fp.name, filetype=filetype) as doc:
            if doc.metadata and doc.metadata["title"]:
                title = doc.metadata["title"]
            else:
                for page in doc:
                    title = page.get_text()[:30]
                    if title:
                        title = title.split("\n", 1)[0]
                        title = title.strip().replace("\r", "")
                        break

            # Prepare the "t" string
            parts = [title]
            if doc.page_count:
                parts.append(f"Pages: {doc.page_count}")
            parts.append(content_type)
            size = convert_size(length)
            parts.append(f"Size: {size}")

            return {
                "@": "http:mupdf",
                "t": ", ".join(parts),

                "title": title,
                "pages": doc.page_count,

                "content_type": content_type,
                "explicit": r.headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA",
                "size": size
            }
