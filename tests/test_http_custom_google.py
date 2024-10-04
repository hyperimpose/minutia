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


class CustomHTTPGoogle(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_search(self):
        u = "https://www.google.com/search?q=test"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["@"], "http:google:search")

        self.assertIsInstance(r[1]["t"], str)
        self.assertGreater(len(r[1]["t"]), 0)

        self.assertFalse(r[1]["snippet"])  # Depends on the query

        self.assertIsInstance(r[1]["results"], list)
        self.assertGreater(len(r[1]["results"]), 0)
        self.assertIsInstance(r[1]["results"][0], dict)
        self.assertIsInstance(r[1]["results"][0]["title"], str)
        self.assertIsInstance(r[1]["results"][0]["link"], str)

        self.assertGreater(r[1]["_ttl"], 0)

    async def test_search_snippet(self):
        u = "https://www.google.com/search?q=how+many+verses+in+greek+anthem"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["@"], "http:google:search")

        self.assertIsInstance(r[1]["snippet"], dict)
        self.assertIsInstance(r[1]["snippet"]["text"], str)
        self.assertIsInstance(r[1]["snippet"]["link"], str)
