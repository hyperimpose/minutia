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
from urllib.parse import urlparse

from . import default, utils


async def handler(link: str, headers):
    return (
        await comments(link, headers)
        or await old(link, headers)
        or False
    )


# ====================================================================
# Thread
# ====================================================================

COMMENTS = re.compile(r"(?i:https?://)?(?i:(www|old)\.)?(?i:reddit.com)/r/.*/comments/.*")  # noqa


async def comments(link: str, headers):
    if not re.fullmatch(COMMENTS, link):
        return False

    u = f"https://www.reddit.com/oembed?url={link}"
    r = await utils.client.get(u, headers=headers)
    j = r.json()

    author_name = j["author_name"]
    title = j["title"]

    # eddit.com is not a mistake
    #
    # We want to split it such that there are two items in the list, even
    # if the link is reddit.com/r/... (it is missing the scheme etc.)
    subreddit = link.split("eddit.com/r/", 1)[1]
    subreddit = subreddit.split("/", 1)[0]

    t = f"/r/{subreddit}: {title}"

    return "ok", {
        "@": "http:reddit:comments",
        "t": t,

        "author_name": author_name,
        "subreddit": subreddit,
        "title": title,

        "_ttl": utils.cache(r.headers)
    }


# ====================================================================
# Generic handler with old.reddit.com redirect
#
# See: https://github.com/tom-james-watson/old-reddit-redirect/blob/master/background.js  # noqa
# ====================================================================

REDDIT = re.compile(r"(?i:https?://)?(?i:(www|np|amp|i)\.)?(?i:reddit.com).*")

old_reddit = "https://old.reddit.com"
excluded_paths = [
    re.compile(r"^/media"),
    re.compile(r"^/poll"),
    re.compile(r"^/rpan"),
    re.compile(r"^/settings"),
    re.compile(r"^/topics"),
    re.compile(r"^/community-points"),
    re.compile(r"^/r/[a-zA-Z0-9_]+/s/.*"),
    re.compile(r"^/appeals?"),
    re.compile(r"^/r/.*/s/")
]


async def old(link: str, headers):
    if not re.fullmatch(REDDIT, link):
        return False

    u = urlparse(link)

    for expath in excluded_paths:
        if re.fullmatch(expath, u.path):
            return

    if u.path.find("/gallery") == 0:
        path = u.path[len('/gallery'):]
        redirect = f"https://old.reddit.com/comments/{path}"
    else:
        redirect = f"https://old.reddit.com{u.path}{u.query}{u.fragment}"

    return await default.get(redirect, headers=headers)
