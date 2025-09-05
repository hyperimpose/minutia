# --------------------------------------------------------------------
# Copyright (C) 2023-2025 hyperimpose.org
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

import html5lib
import xml.etree.ElementTree as ET

from minutia import common, config
from . import heurestics, override


async def handle(r):
    max_htmlsize = override.max_htmlsize(str(r.url)) or config.max_htmlsize

    data = b""
    async for chunk in r.aiter_bytes():
        data += chunk
        if len(data) > max_htmlsize:
            break

    return await get_title(data, r.headers, encoding=r.encoding)


async def get_title(data, headers, encoding="utf-8"):
    document = html5lib.parse(data,
                              transport_encoding=encoding,
                              namespaceHTMLElements=False)

    special = await heurestics.apply(document, headers)
    if special:
        if "explicit" not in special:
            special.update({"explicit": is_explicit(document, headers)})
        return special

    title = _get_title(document)
    if not title:
        return False

    return {
        "@": "http:html",
        "t": common.cleanup(title),

        "explicit": is_explicit(document, headers)
    }


def _get_title(document):
    # HTML <title>
    title = document.find(".//title")
    if title is not None:
        return title.text

    # <meta> title
    title = document.find(".//meta[@name='title']")
    if title is not None:
        return title.attrib["content"]

    # oEmbed title
    title = document.find(".//link[@type='application/json+oembed']")
    if title is not None:
        return title.attrib["title"]

    title = document.find(".//link[@type='application/xml+oembed']")
    if title is not None:
        return title.attrib["title"]

    title = document.find(".//link[@type='text/xml+oembed']")
    if title is not None:
        return title.attrib["title"]

    # Open Graph
    title = document.find(".//meta[@property='og:title']")
    if title is not None:
        return title.attrib["content"]

    # Twitter Cards
    title = document.find(".//meta[@name='twitter:title']")
    if title is not None:
        return title.attrib["content"]

    # Dublin Core
    title = document.find(".//meta[@name='DC.Title']")
    if title is not None:
        return title.attrib["content"]

    # Search for class attributes
    title = document.find(".//*[@class='title']")
    if title is not None:
        title_l = ET.tostringlist(title, encoding="unicode", method="text")
        title_l = [x.strip() for x in title_l]
        return " ".join(title_l)

    # Search for id attributes
    title = document.find(".//*[@id='title']")
    if title is not None:
        title_l = ET.tostringlist(title, encoding="unicode", method="text")
        title_l = [x.strip() for x in title_l]
        return " ".join(title_l)

    return ""


def is_explicit(document, headers):
    rating = document.find(".//meta[@name='rating']")
    if rating:
        c = rating.attrib["content"]
        explicit = (c == "adult") or (c == "RTA-5042-1996-1400-1577-RTA")
    else:
        explicit = headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA"

    return float(explicit)
