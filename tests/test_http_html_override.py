# --------------------------------------------------------------------
# Copyright (C) 2025 hyperimpose.org
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


class HTTP_HTML_Override(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_github_file(self):
        u = "https://github.com/hyperimpose/minutia/blob/master/README.org"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")

        self.assertEqual(r[1]["@"], "http:html")
        self.assertEqual(r[1]["t"], "minutia/README.org at master · hyperimpose/minutia · GitHub")  # noqa
