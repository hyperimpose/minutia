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

import unittest

import minutia  # type: ignore


class CustomHTTPLainchan(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_thread(self):
        u = "https://lainchan.org/%CE%BB/res/1.html"
        r = await minutia.http.get(u)
        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:lainchan:thread")
        self.assertEqual(r[1]["t"], "The Sticky: /λ/ 2.0")

        self.assertEqual(r[1]["title"], "The Sticky: /λ/ 2.0")
        self.assertEqual(r[1]["board"], "%CE%BB")
        self.assertEqual(r[1]["replies"], 0)
        self.assertEqual(r[1]["files"], 1)
        self.assertEqual(
            r[1]["post"],
            ("This is new /λ/, also addressable as /lambda/, the"
             " programming board.  The intent is that this board will"
             " be used to share and discuss programs that h...")
        )

        self.assertGreater(r[1]["_ttl"], 0)

    async def test_mod_thread(self):
        u = "https://lainchan.org/mod.php?/%CE%A9/res/73638.html#76881"
        r = await minutia.http.get(u)
        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:html")
        self.assertEqual(r[1]["t"], "Login")

        self.assertEqual(r[1]["explicit"], 0.0)
