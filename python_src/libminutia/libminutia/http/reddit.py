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
# Thread
# ====================================================================

COMMENTS = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:reddit.com)/r/.*/comments/.*")


async def comments(url: str, _headers):
    if not re.fullmatch(COMMENTS, url):
        return False

    u = f"https://www.reddit.com/oembed?url={url}"
    r = await utils.client.get(u)
    j = r.json()

    author_name = j["author_name"]
    title = j["title"]

    # eddit.com is not a mistake
    #
    # We want to split it such that there are two items in the list, even
    # if the url is reddit.com/r/... (it is missing the scheme etc.)
    subreddit = url.split("eddit.com/r/", 1)[1]
    subreddit = subreddit.split("/", 1)[0]

    t = f"/r/{subreddit}: {title}"

    return "ok", {
        "@": "http:reddit:comments",
        "t": t,

        "title": title,
        "author_name": author_name,
        "subreddit": subreddit,

        "_ttl": utils.cache(r.headers)
    }
