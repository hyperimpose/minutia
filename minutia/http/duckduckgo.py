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
import re
from urllib.parse import parse_qs, urlparse

import html5lib

from . import utils


logger = logging.getLogger(__name__)


# ====================================================================
# Search
# ====================================================================

SEARCH = re.compile(r"(?i:https?://)?(?i:html.duckduckgo.com)/html\?q=.*")


async def search(url: str, headers):
    if not re.fullmatch(SEARCH, url):
        return False

    headers["User-Agent"] = "w3m"  # Helps avoid captcha

    # Adding this 'magic' string makes duckduckgo return output that is
    # easier to extract information from.
    magic = "&kl=wt-wt&kp=-2&kaf=1&kh=1&k1=-1&kd=-1"

    q = "".join(parse_qs(urlparse(url).query).get("q", ""))
    u = f"https://html.duckduckgo.com/html?q={q}" + magic

    r = await utils.client.get(u, headers=headers)
    d = html5lib.parse(r.text, namespaceHTMLElements=False)

    title = d.find(".//title").text.strip()

    links = []
    for a in d.findall(".//a[@class='result__url']"):
        links.append(a.attrib["href"].strip())

    titles = []
    for h2 in d.findall(".//h2[@class='result__title']"):
        titles.append("".join(h2.itertext()).strip())

    captions = []
    for a in d.findall(".//a[@class='result__snippet']"):
        captions.append("".join(a.itertext()).strip())

    results = []
    if len(links) == len(titles) == len(captions):
        for link, t, c in zip(links, titles, captions):
            results.append({
                "link": link,
                "title": t,
                "caption": c
            })
    else:
        logger.error("[minutia] Incomplete results for %s", url)

    return "ok", {
        "@": "http:duckduckgo:search",
        "t": title,
        "results": results,
        "_ttl": utils.cache(r.headers)
    }
