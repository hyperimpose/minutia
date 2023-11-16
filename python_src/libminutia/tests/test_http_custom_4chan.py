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

import unittest

import libminutia  # type: ignore


class CustomHTTP4chan(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await libminutia.init()

    async def asyncTearDown(self):
        await libminutia.terminate()

    async def test_i_4cdn_sfw(self):
        u = "https://i.4cdn.org/g/1594686780709.png"
        r = await libminutia.http.get(u)
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "image/png, 535x420, Size: 300.06 KB")
        self.assertEqual(r[1]["explicit"], False)

    async def test_is2_4chan_sfw(self):
        u = "https://is2.4chan.org/g/1594686780709.png"
        r = await libminutia.http.get(u)
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "image/png, 535x420, Size: 300.06 KB")
        self.assertEqual(r[1]["explicit"], False)

    async def test_i_4cdn_nsfw(self):
        u = "https://i.4cdn.org/pol/1493993226750.jpg"
        r = await libminutia.http.get(u)
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "image/jpeg, 1600x1131, Size: 627.27 KB")
        self.assertEqual(r[1]["explicit"], True)

    async def test_is2_4chan_nsfw(self):
        u = "https://is2.4chan.org/pol/1493993226750.jpg"
        r = await libminutia.http.get(u)
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "image/jpeg, 1600x1131, Size: 627.27 KB")
        self.assertEqual(r[1]["explicit"], True)
