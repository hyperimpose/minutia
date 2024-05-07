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

import re
import xml.etree.ElementTree as ET

import html5lib

from . import utils


# ====================================================================
# Thread
# ====================================================================

TWEET = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:(twitter|x).com)/.*/status/.*")  # noqa


async def tweet(url: str, _headers):
    if not re.fullmatch(TWEET, url):
        return False

    u = f"https://publish.twitter.com/oembed?url={url}"
    r = await utils.client.get(u)
    j = r.json()

    html = j["html"]
    d = html5lib.parse(html, namespaceHTMLElements=False)
    tweet_l = ET.tostringlist(d, encoding="unicode", method="text")
    tweet_l = [x.strip() for x in tweet_l]
    tweet = " ".join(tweet_l).strip()

    return "ok", {
        "@": "http:twitter:tweet",
        "t": tweet,

        "_ttl": utils.cache(r.headers)
    }
