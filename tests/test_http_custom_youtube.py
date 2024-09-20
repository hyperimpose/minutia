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

import minutia  # type: ignore


class CustomHttpYouTube(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_video(self):
        u = "https://www.youtube.com/watch?v=rdwz7QiG0lk"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:youtube:video")
        self.assertEqual(r[1]["t"], "YouTube on the tube!")

        self.assertEqual(r[1]["title"], "YouTube on the tube!")
        self.assertEqual(r[1]["author_name"], "YouTube")
        self.assertEqual(r[1]["author_url"], "https://www.youtube.com/@YouTube")
        self.assertEqual(r[1]["type"], "video")
        self.assertEqual(r[1]["height"], 150)
        self.assertEqual(r[1]["width"], 200)
        self.assertEqual(r[1]["thumbnail_url"], "https://i.ytimg.com/vi/rdwz7QiG0lk/hqdefault.jpg")
        self.assertEqual(r[1]["thumbnail_height"], 360)
        self.assertEqual(r[1]["thumbnail_width"], 480)
        self.assertIn("<iframe ", r[1]["html"])

        self.assertGreater(r[1]["_ttl"], 0)

    async def test_search(self):
        u = "https://www.youtube.com/results?search_query=Kelly+Moran+Helix"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:youtube:search")
        self.assertEqual(r[1]["t"], "Kelly Moran Helix - YouTube")

        self.assertIsInstance(r[1]["results"], list)

        self.assertGreater(r[1]["_ttl"], 0)
