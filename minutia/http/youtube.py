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
import json
import logging
import urllib.parse

from . import utils


logger = logging.getLogger(__name__)


async def handler(link: str, headers):
    return (
        await video(link)
        or await search(link, headers)
        or await fallback(link)
        or False
    )


# ====================================================================
# Video
# ====================================================================

LIVE = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:youtube\.com)/live/.*")
VID = re.compile(r"(?i:https?://)?(?i:(www|m|music)\.)?(?i:youtube\.com)/watch\?v=.*")  # noqa
VID_SHORT = re.compile(r"(?i:https?://)?(?i:youtu\.be)/.*")


async def video(url: str):
    """Return information about a youtube video."""

    if not (re.fullmatch(VID, url) or re.fullmatch(VID_SHORT, url)
            or re.fullmatch(LIVE, url)):
        return False

    u = f"https://www.youtube.com/oembed?url={url}"
    r = await utils.client.get(u)

    if r.status_code != 200:
        return False

    j = r.json()

    return "ok", {
        "@": "http:youtube:video",
        "t": j["title"],

        "author_name": j["author_name"],
        "author_url": j["author_url"],
        "height": j["height"],
        "html": j["html"],
        "thumbnail_height": j["thumbnail_height"],
        "thumbnail_url": j["thumbnail_url"],
        "thumbnail_width": j["thumbnail_width"],
        "title": j["title"],
        "type": j["type"],
        "width": j["width"],

        "_ttl": utils.cache(r.headers)
    }


# ====================================================================
# Search
# ====================================================================

SEARCH = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:youtube\.com)/results\?search_query=.*")  # noqa


async def search(url: str, headers: dict = {}):
    if not re.fullmatch(SEARCH, url):
        return False

    r = await utils.client.get(url, headers=headers)

    try:
        st = 'var ytInitialData = '
        st_i = r.text.index(st) + len(st)
    except ValueError:
        st = 'window["ytInitialData"] = '
        st_i = r.text.index(st) + len(st)

    j_data = r.text[st_i:]

    st = '};'
    st_i = j_data.index(st)

    j_data = j_data[:st_i+1]
    j = json.loads(j_data)

    sections = filter(lambda x: "itemSectionRenderer" in x,
                      (j["contents"]
                       ["twoColumnSearchResultsRenderer"]
                       ["primaryContents"]
                       ["sectionListRenderer"]
                       ["contents"]))
    item_lists = map(lambda x: x["itemSectionRenderer"]["contents"], sections)
    items = [i for item_list in item_lists for i in item_list]  # flatten
    videos = filter(lambda x: "videoRenderer" in x, items)  # filter ads/shorts
    results = list(map(lambda x: s_vid_info(x["videoRenderer"]), videos))

    t = urllib.parse.unquote_plus(url.split("=", 1)[1]) + " - YouTube"

    return "ok", {
        "@": "http:youtube:search",
        "t": t,

        "results": results,

        "_ttl": utils.cache(r.headers)
    }


def s_vid_info(v):
    yt_id = v["videoId"]
    short_url = f"https://youtu.be/{yt_id}"
    name = v["title"]["runs"][0]["text"]
    # Usually youtube's automated music uploads do not have dates.
    try:
        date = v["publishedTimeText"]["simpleText"]
    except KeyError:
        date = ""
    # For unknown reasons sometimes we cannot find the duration.
    try:
        duration = v["lengthText"]["simpleText"]
    except KeyError:
        logger.warning("[minutia:youtube] Unable to find duration in %s", v)
        duration = ""
    # For unknown reasons sometimes we cannot find the views.
    try:
        views = v["viewCountText"]["simpleText"]
    except KeyError:
        logger.warning("[minutia:youtube] Unable to find views in %s", v)
        views = ""

    channel = v["ownerText"]["runs"][0]["text"]

    return {
        "short_url": short_url, "name": name, "date": date, "views": views,
        "channel": channel, "duration": duration, "yt_id": yt_id
    }


# ====================================================================
# Fallback
# ====================================================================

YT = re.compile(r"(?i:https?://)?(?i:.*\.youtube\.com)/.*")


async def fallback(link: str):
    if not re.fullmatch(YT, link):
        return False

    u = urllib.parse.urlparse(link)

    p = u.path[1:].split("/")
    if not p or not p[0]:       # https://*.youtube.com/
        t = "YouTube"
    elif p[0].startswith("@"):  # Channels
        t = p[0] + " " + " ".join(p[1:]).title() + " - YouTube"
    else:                       # Rest
        t = " ".join(p).title() + " - YouTube"

    return "ok", {
        "@": "http:html",
        "t": t,

        "explicit": 0.0  # No info on explicity
    }
