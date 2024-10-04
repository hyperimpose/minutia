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

# The following tests are based on https://irc-bot-science.clsr.net/

import unittest

import minutia  # type: ignore


class IrcBotScience(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_carriage_return(self):
        u = "https://irc-bot-science.clsr.net/test"
        r = await minutia.http.get(u)

        t = "test QUIT :Look at me, I'm an IRC bot with security holes! (ignore this if it's all in one line)"
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], t)

    async def test_uncommon(self):
        u = "https://irc-bot-science.clsr.net/tags"
        r = await minutia.http.get(u)
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "this is a site <title>")

    async def test_uncommon_hard(self):
        u = "https://irc-bot-science.clsr.net/hardmode"
        r = await minutia.http.get(u)

        t = "this is a <title> site title < /title> but <title> not just this part</title>"
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], t)

    async def test_notitle(self):
        u = "https://irc-bot-science.clsr.net/notitle"
        r = await minutia.http.get(u)

        self.assertEqual(r, False)

    # Skipped the long title test. This is the responsibility of the caller.
    # Length is handled by the max_htmlsize config option.

    async def test_large_filesize(self):
        u = "https://irc-bot-science.clsr.net/internet.gz"
        r = await minutia.http.get(u)

        t = "the-internet.gz, application/x-gzip, Size: 1.1 EB"
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], t)

    async def test_ctcp_messages(self):
        u = "https://irc-bot-science.clsr.net/ctcp"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], "ACTION is a shit bot")

    async def test_redirect(self):
        u = "https://irc-bot-science.clsr.net/redirect"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "error")
        self.assertEqual(r[1], "The page isn’t redirecting properly")

    async def test_redirect_to_other_urls(self):
        u = "https://irc-bot-science.clsr.net/redirect/0"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "error")
        self.assertEqual(r[1], "The page isn’t redirecting properly")

    async def test_1gb_html_fake_content_length(self):
        u = "https://irc-bot-science.clsr.net/fakelength"
        r = await minutia.http.get(u)

        self.assertEqual(r, False)

    async def test_1gb_html_with_title(self):
        u = "https://irc-bot-science.clsr.net/large"
        r = await minutia.http.get(u)

        t = "If this title is printed, it works correctly."
        self.assertEqual(r[0], "ok")
        self.assertEqual(r[1]["t"], t)

    async def test_1gb_headers(self):
        u = "https://irc-bot-science.clsr.net/longheaders"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "error")

    async def test_extremely_long_header(self):
        u = "https://irc-bot-science.clsr.net/bigheader"
        r = await minutia.http.get(u)

        self.assertEqual(r[0], "error")
