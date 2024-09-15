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

from typing import Any, Callable, Coroutine, Literal

import httpx

from minutia import config
from minutia.http import (
    # Default handler
    default,
    # Custom handlers
    fourchan, lainchan, reddit, twitter, youtube
)

# ====================================================================
# Types
# ====================================================================

Headers = dict[str, str]
OkDict = dict[str, str | int | bool | None]
ReturnT = (tuple[Literal["ok"], OkDict]
           | Literal[False]
           | tuple[Literal["error"], str, Exception])

CustomHandler = Callable[[str, Headers], Coroutine[Any, Any, ReturnT]]


# ====================================================================
# API
# ====================================================================

async def get(link: str, lang="") -> ReturnT:
    headers = {
        "Accept-Language": lang or config.lang,
        "User-Agent": config.http_useragent
    }

    try:
        return (
            await get_custom(link, headers=headers)
            or await default.get(link, headers=headers)
            or False
        )
    except httpx.NetworkError as e:
        return ("error", "Can't connect to this address", e)
    except httpx.TimeoutException as e:
        return ("error", "The connection timed out", e)
    except httpx.TooManyRedirects as e:
        return ("error", "The page isn’t redirecting properly", e)
    except httpx.HTTPError as e:
        return ("error", "Can't complete the request", e)
    except Exception as e:
        # Unknown exceptions indicate an unexpected error, possibly
        # a bug with libminutia.
        # We return an empty user message to indicate this to the caller.
        return ("error", "", e)


# ====================================================================
# Custom
# ====================================================================

handler_l: list[CustomHandler] = [
    fourchan.file, lainchan.thread, reddit.handler, twitter.tweet,
    youtube.handler
]


async def get_custom(link: str, headers: Headers = {}):
    """
    Try to find a title for the given link using a customized method.

    This method is preferable for some links because:
    1) It may require specialized methods for title extraction.
    2) We may want to get more than just the title.
    3) It may be faster to handle the service with a custom mechanism.
    """
    for handler in handler_l:
        ret = await handler(link, headers)
        if ret:
            return ret

    return False
