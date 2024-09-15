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

from email.utils import parsedate_to_datetime

from minutia import common


def age(headers):
    s = headers.get("Age", None)
    if not s:
        return None

    try:
        age = int(s)
        if age < 0:
            return None
        else:
            return age
    except ValueError:
        return None


def cache_control(headers):
    dir_s = headers.get("Cache-Control", "")

    dir_l = [x.strip() for x in dir_s.lower().split(",")]
    dir_l = [x.split("=", 1) for x in dir_l if x]

    directives = {}
    for d in dir_l:
        if len(d) == 2:
            k, v = d
            if (k not in directives) or (v < directives[k]):
                directives[k] = v
        else:
            directives[d[0]] = None

    return directives


def date(headers):
    date = headers.get("Date", None)
    if not date:
        return None

    try:
        return parsedate_to_datetime(date).timestamp()
    except ValueError:
        return None


def expires(headers):
    s = headers.get("Expires", None)
    if not s:
        return None

    try:
        return parsedate_to_datetime(s).timestamp()
    except ValueError:
        return None


def filename(headers):
    # The following is not RFC 6266 compliant.
    # Use a library if there are issues.
    filename = headers.get("Content-Disposition", "").split("=")[-1]
    filename = filename.replace("/", "_").replace("\\", "_")  # Sanitize
    if filename and filename[0] == '"' and filename[-1] == '"':
        filename = filename[1:-1]

    return filename or None


def filesize(headers):
    length = headers.get("content-length", None)
    if length:
        return common.convert_size(length)
    else:
        return None


def last_modified(headers):
    lm = headers.get("Last-Modified", None)
    if not lm:
        return None

    try:
        return parsedate_to_datetime(lm).timestamp()
    except ValueError:
        return None


def mimetype(headers):
    s = headers.get("content-type", None)
    if not s:
        return None

    return s.split(";", 1)[0]  # remove any parameters
