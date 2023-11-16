# --------------------------------------------------------------------
# Copyright (C) 2023 hyperimpose.org
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
import urllib.parse

from . import utils


# ====================================================================
# Video
# ====================================================================

LIVE = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:youtube\.com)/live/.*")
VID = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:youtube\.com)/watch\?v=.*")
VID_SHORT = re.compile(r"(?i:https?://)?(?i:youtu\.be)/.*")


async def video(url: str, _headers):
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

        "title": j["title"],
        "author_name": j["author_name"],
        "author_url": j["author_url"],
        "type": j["type"],
        "height": j["height"],
        "width": j["width"],
        "thumbnail_url": j["thumbnail_url"],
        "thumbnail_height": j["thumbnail_height"],
        "thumbnail_width": j["thumbnail_width"],
        "html": j["html"],

        "_ttl": utils.cache(r.headers)
    }


# ====================================================================
# Search
# ====================================================================

SEARCH = re.compile(r"(?i:https?://)?(?i:www\.)?(?i:youtube\.com)/results\?search_query=.*")


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

    results = (j["contents"]
               ['twoColumnSearchResultsRenderer']
               ['primaryContents']
               ['sectionListRenderer']
               ['contents']
               [0]
               ['itemSectionRenderer']
               ['contents'])  # What in the world?

    videos = []
    for result in results:
        if "videoRenderer" in result:
            v = result["videoRenderer"]  # Video information
            videos.append(s_vid_info(v))
        elif 'searchPyvRenderer' in result:
            continue  # Skip promoted videos

    t = urllib.parse.unquote_plus(url.split("=", 1)[1]) + " - YouTube"

    return "ok", {
        "@": "http:youtube:search",
        "t": t,

        "results": videos,

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
        date = False
    duration = v["lengthText"]["simpleText"]
    views = v["viewCountText"]["simpleText"]
    channel = v["ownerText"]["runs"][0]["text"]

    return {
        "short_url": short_url, "name": name, "date": date, "views": views,
        "channel": channel, "duration": duration, "yt_id": yt_id
    }
