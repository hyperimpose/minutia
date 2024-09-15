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

import time
from typing import Any

from minutia import common
from . import hparser


client: Any


# ====================================================================
# Cache
# ====================================================================

# It does not do actual content caching. We are just calculating a time
# from some of the headers.
#
# This cache implementation is NOT standards compliant and is not meant
# to be used for doing revalidation.

def cache(headers):
    cc = _cache_control(headers)
    if cc is not None:
        return int(time.time() + cc)

    ttl = hparser.expires(headers)
    if ttl is not None:
        return int(ttl)

    # 0.1 * the time elapsed since the site was last modified
    # 5 minutes minimum
    lm = hparser.last_modified(headers)
    if lm is not None:
        now = time.time()
        return int(now + ((now - lm) * 0.1))

    return None


def _cache_control(headers):
    d = hparser.cache_control(headers)
    if not d:
        return None

    ttl = 0

    if "max-age" in d:
        try:
            ttl += int(d["max-age"])
        except ValueError:
            pass

    # Because revalidation is not supported we just increment
    # the ttl by a small part of this directive's value
    if "stale-while-revalidate" in d:
        try:
            ttl += int(d["stale-while-revalidate"]) * 0.1
        except ValueError:
            pass

    age = hparser.age(headers)
    if age:
        return ttl - age

    date = hparser.date(headers)
    if date:
        return ttl - (time.time() - date)

    return ttl


# ====================================================================
# Explicit
# ====================================================================

async def get_explicit(r, path="", duration=0) -> float:
    if r.headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA":
        return 1.0

    if not path:
        return 0.0

    mimetype = hparser.mimetype(r.headers)
    if "image/" in mimetype:
        return await common.image_explicit_score(path)
    elif "video/" in mimetype:
        return await common.video_explicit_score(path, duration=duration)
    else:
        return 0.0
