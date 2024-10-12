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

SEARCH = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:bing.com)/search\?.*")


async def search(url: str, headers):
    if not re.fullmatch(SEARCH, url):
        return False

    r = await utils.client.get(url, headers=headers, follow_redirects=True)
    d = html5lib.parse(r.text, namespaceHTMLElements=False)

    title = d.find(".//title").text

    results = []
    for li in d.findall(".//li[@class='b_algo']"):
        a = li.find(".//h2").find(".//a")
        results.append({
            "link": a.attrib["href"],
            "title": "".join(a.itertext()),
            "description": "".join(li.find(".//p").itertext())[3:]
        })

    return "ok", {
        "@": "http:bing:search",
        "t": title,
        "results": results,
        "_ttl": utils.cache(r.headers)
    }
