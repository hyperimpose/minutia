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

from libminutia.common import convert_size


async def handle(_url, r):
    content_type = r.headers.get("content-type", "application/octet-stream")
    length = r.headers.get("content-length", None)
    explicit = r.headers.get("rating", "") == "RTA-5042-1996-1400-1577-RTA"

    # The following is not RFC 6266 compliant.
    # Use a library if there are issues.
    filename = r.headers.get("Content-Disposition", "").split("=")[-1]
    filename = filename.replace("/", "_").replace("\\", "_")  # Sanitize
    if filename and filename[0] == '"' and filename[-1] == '"':
        filename = filename[1:-1]

    t = []
    if filename:
        t.append(filename)

    t = ", ".join([*t, content_type])

    size = None
    if length:
        size = convert_size(length)
        t += f", Size: {size}"

    return {
        "@": "http:fallback",
        "t": t,

        "content_type": content_type,
        "filename": filename or None,
        "explicit": explicit,
        "size": size
    }
