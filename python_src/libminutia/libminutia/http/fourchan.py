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

from . import default, utils


# ====================================================================
# Initialization [internal use only]
# ====================================================================

BOARDS = None


async def init():
    global BOARDS

    boards_url = "https://a.4cdn.org/boards.json"

    r = await utils.client.get(boards_url)
    j = r.json()

    BOARDS = j["boards"]


async def is_worksafe(board):
    if not BOARDS:
        await init()

    board = board.lower()

    for i in BOARDS:
        if i["board"] == board:
            return i["ws_board"] == 1

    return None


# ====================================================================
# File
# ====================================================================

I_4CDN = re.compile(r"(?i:https?://)?(?i:i.4cdn.org)/.*")
I_4CDN_BOARD = re.compile(r"i.4cdn.org/+([^/]*)")
IS2_4CHAN = re.compile(r"(?i:https?://)?(?i:is2.4chan.org)/.*")
IS2_4CHAN_BOARD = re.compile(r"is2.4chan.org/+([^/]*)")


async def file(url: str, _headers):
    if not (re.fullmatch(I_4CDN, url) or re.fullmatch(IS2_4CHAN, url)):
        return False

    board_m = re.search(I_4CDN_BOARD, url) or re.search(IS2_4CHAN_BOARD, url)
    if not board_m:
        return False

    board = board_m.group(1)
    if not board:
        return False

    match await default.get(url):
        case "ok", result:
            if not (await is_worksafe(board)):
                result["explicit"] = 1.0
            return "ok", result
        case Else:
            return Else
