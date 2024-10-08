# --------------------------------------------------------------------
# Copyright (C) 2024 hyperimpose.org
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

import unittest

import minutia  # type: ignore


class CustomHTTPDuckDuckGo(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_search(self):
        u = "https://html.duckduckgo.com/html?q=irc"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:duckduckgo:search")

        self.assertIsInstance(r[1]["t"], str)
        self.assertGreater(len(r[1]["t"]), 0)

        self.assertIsInstance(r[1]["results"], list)
        self.assertGreater(len(r[1]["results"]), 0)
        self.assertIsInstance(r[1]["results"][0], dict)
        self.assertIsInstance(r[1]["results"][0]["title"], str)
        self.assertIsInstance(r[1]["results"][0]["link"], str)
        self.assertIsInstance(r[1]["results"][0]["description"], str)

        self.assertGreater(r[1]["_ttl"], 0)
