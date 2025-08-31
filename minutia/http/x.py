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

import re
import xml.etree.ElementTree as ET

import html5lib

from . import utils


# ====================================================================
# Thread
# ====================================================================

STATUS = re.compile(r"(?i:https?://)?(?i:(www|mobile)\.)?(?i:(twitter|x).com)/.+/status/.*")  # noqa
PROFILE = re.compile(r"(?i:https?://)?(?i:(www|mobile)\.)?(?i:(twitter|x).com)/[^/]+/?")  # noqa


async def handler(url: str, _headers):
    if not re.fullmatch(STATUS, url) and not re.fullmatch(PROFILE, url):
        return False

    # For tweets remove everything after the X ID, so the oembed API works
    # IDs are integers according to https://docs.x.com/fundamentals/x-ids
    url = re.sub(r'(/status/\d+).*', r'\1', url)

    u = f"https://publish.twitter.com/oembed?url={url}"
    r = await utils.client.get(u)
    j = r.json()

    html = j["html"]
    d = html5lib.parse(html, namespaceHTMLElements=False)
    text_l = ET.tostringlist(d, encoding="unicode", method="text")
    text_l = [x.strip() for x in text_l]
    text = " ".join(text_l).strip()

    return "ok", {
        "@": "http:x",
        "t": text,

        "_ttl": utils.cache(r.headers)
    }
