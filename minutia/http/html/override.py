# --------------------------------------------------------------------
# Copyright (C) 2025 hyperimpose.org
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


MAX_HTMLSIZE = {
    # Github Files
    re.compile(r"(?i:https?://)?(?i:www\.)?(?i:github\.com)/.*/.*/.*"): 35_000
}


def max_htmlsize(url: str) -> int | None:
    for key, value in MAX_HTMLSIZE.items():
        if re.fullmatch(key, url):
            return value

    return None
