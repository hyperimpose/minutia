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

import re

import html5lib

from . import utils


# ====================================================================
# Search
# ====================================================================

SEARCH = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:google.com)/search\?.*")


async def search(url: str, headers):
    if not re.fullmatch(SEARCH, url):
        return False

    r = await utils.client.get(url, headers=headers, follow_redirects=True)
    d = html5lib.parse(r.text, namespaceHTMLElements=False)

    title = d.find(".//title").text

    answer = {}
    bc = d.find(".//block-component")
    if bc is not None:
        span = bc.find(".//span")
        if span is not None:  # No point in having a link without the text
            answer["text"] = "".join(span.itertext())
            a = bc.find(".//a")
            answer["link"] = a.attrib["href"] if a is not None else ""

    results = []
    div = d.find(".//div[@id='search']")
    if div is not None:
        for a in div.findall(".//a"):
            h3 = a.find("h3")
            results.append({
                "link": a.attrib["href"],
                "title": h3.text if h3 is not None else ""})

    return "ok", {
        "@": "http:google:search",
        "t": title,
        "answer": answer,    # may be empty -> {}
        "results": results,  # may be empty -> []
        "_ttl": utils.cache(r.headers)
    }
