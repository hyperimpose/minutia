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


class CustomHttpReddit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_comments(self):
        u = ("https://www.reddit.com/r/Showerthoughts/comments/"
             "2safxv/we_should_start_keeping_giraffes_a_secret_from/cno7zic")
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:reddit:comments")
        self.assertEqual(r[1]["t"], '/r/Showerthoughts: We should start keeping giraffes a secret from young children. Imagine discovering giraffes exist when you were like 15. "Woah! Check out that long necked horse!"')

        self.assertEqual(r[1]["title"], 'We should start keeping giraffes a secret from young children. Imagine discovering giraffes exist when you were like 15. "Woah! Check out that long necked horse!"')
        self.assertEqual(r[1]["author_name"], "yankeltank")
        self.assertEqual(r[1]["subreddit"], "Showerthoughts")

        self.assertGreater(r[1]["_ttl"], 0)
