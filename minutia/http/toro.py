# --------------------------------------------------------------------
# Copyright (C) 2026 hyperimpose.org
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

from . import default


# ====================================================================
# Thread
# ====================================================================

U_FILE = re.compile(r"(?i:https?://)?(?i:toro.lain.la)/u/.*")


async def handler(url: str, headers):
    if not re.fullmatch(U_FILE, url):
        return False

    f_url = url.replace("/u/", "/f/", 1)

    match await default.get(f_url, headers):
        case False:
            return False
        case "ok", response:
            return "ok", {
                "@": "http:toro.lain.la",
                "t": response.get("t", ""),

                "direct": f_url,

                "explicit": response.get("explicit", 0.0),
                "_ttl": response.get("_ttl")
            }
