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

from . import nitter


og_site_name = {
    "Nitter": nitter.title
}


async def apply(document, headers):
    try:
        return await _apply(document, headers)
    except Exception:
        return False


async def _apply(document, headers):
    # Open Graph
    site_name = document.find("./head/meta[@property='og:site_name']")
    if site_name is not None:
        site_name = site_name.attrib["content"]

        handler = og_site_name.get(site_name, None)
        if handler is not None:
            return await handler(document, headers)

    return False
