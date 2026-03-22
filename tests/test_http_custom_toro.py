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

import unittest

import minutia  # type: ignore


class CustomHTTPToro(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_vomit(self):
        u = "https://toro.lain.la/u/6IQqTw.png"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:toro.lain.la")
        self.assertEqual(r[1]["t"], "image/png, 1024x768, Size: 45.61 KB")

        self.assertEqual(r[1]["direct"], "https://toro.lain.la/f/6IQqTw.png")

        self.assertEqual(r[1]["explicit"], 0.0)
        self.assertGreater(r[1]["_ttl"], 0)
