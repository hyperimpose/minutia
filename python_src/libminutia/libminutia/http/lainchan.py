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

THREAD = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:lainchan\.org)/.*/res/.*")
MOD = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:lainchan\.org)/mod.php.*")


async def thread(url: str, _headers):
    if re.fullmatch(MOD, url):  # Ignore moderator paths
        return False

    if not re.fullmatch(THREAD, url):
        return False

    # Extract info from the URL
    board = url.split("lainchan.org/")[1].split("/", 1)[0]

    url_l = url.rsplit("#", 1)
    if len(url_l) > 0:
        post_no = re.sub(r"\D", "", url_l[-1])  # Remove non digit characters
    else:
        post_no = ""

    # Prepare the JSON URL
    u = url_l[0]
    if u[-5:] == ".html":
        u = u[:-5]

    u = f"{u}.json"

    # HTTP Request
    r = await utils.client.get(u)
    if r.status_code != 200:
        return False

    j = r.json()

    post = j["posts"][0]  # Set the OP as the target post

    # Title
    if "sub" in post:
        title = post["sub"]

    if post_no:
        for i in j["posts"]:
            if int(post_no) == i["no"]:
                post = i
                break

    d = html5lib.parse(post["com"], namespaceHTMLElements=False)
    post_l = ET.tostringlist(d, encoding="unicode", method="text")
    post = " ".join(post_l)[:150] + "..."

    # File count
    files = 0
    for i in j["posts"]:
        if "filename" in i:
            files += 1
        if "extra_files" in i:
            files += len(i["extra_files"])

    # Reply count
    replies = len(j["posts"]) - 1

    return "ok", {
        "@": "http:lainchan:thread",
        "t": title,

        "board": board,
        "files": files,
        "post": post,
        "replies": replies,
        "title": title,

        "_ttl": utils.cache(r.headers)
    }
