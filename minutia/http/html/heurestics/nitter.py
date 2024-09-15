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

async def title(document, _headers):
    title = document.find("./head/meta[@property='og:title']")
    if title is not None:
        title = title.attrib["content"]

    description = document.find("./head/meta[@property='og:description']")
    if description is not None:
        description = description.attrib["content"]

    return {
        "@": "http:nitter",
        "t": title,

        "description": description
        # explicit is added by the caller
    }
