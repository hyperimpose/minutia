"""libminutia summarizes the content of various internet services"""

__version__ = "0.2"


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

import httpx

from minutia import common, config, http
from services import explicit


# ====================================================================
# System
# ====================================================================

async def init():
    http.utils.client = httpx.AsyncClient()


async def terminate():
    await http.utils.client.aclose()
    await setup_explicit_unix_socket("")


# ====================================================================
# Config
# ====================================================================

def set_lang(lang: str):
    config.lang = lang


def set_max_htmlsize(i: int):
    config.max_htmlsize = i


def set_max_filesize(i: int):
    config.max_filesize = i


def set_http_useragent(ua: str):
    config.http_useragent = ua


# ====================================================================
# Setup
# ====================================================================

async def setup_explicit_unix_socket(path: str):
    if path:
        common.explicit.client = explicit.UnixClient(path)
        await common.explicit.client.connect()
    else:
        if common.explicit.client:
            await common.explicit.client.close()
            common.explicit.client = None
