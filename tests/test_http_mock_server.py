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

import contextlib
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import minutia  # type: ignore


class HTTPMisc(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await minutia.init()

    async def asyncTearDown(self):
        await minutia.terminate()

    async def test_stale_while_revalidate_without_value(self):
        settings = {
            "headers": {"Cache-Control": "s-maxage=45, stale-while-revalidate"}
        }
        with run_test_server(settings) as url:
            r = await minutia.http.get(url)
            self.assertEqual(r[0], "ok")


# ====================================================================
# Helpers
# ====================================================================

@contextlib.contextmanager
def run_test_server(settings: dict):
    handler = make_handler(**settings)

    server = HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def make_handler(
        *,
        status=200,
        body=b'',
        headers: dict[str, str] = {}
):
    class TestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(status)

            for header, value in headers.items():
                self.send_header(header, value)
            self.end_headers()

            self.wfile.write(body)

        def log_message(self, format, *args):
            return  # silence logs

    return TestHandler
