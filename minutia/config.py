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


# General Settings
lang = "en"  # Default language used

# The following default is based on the TCP slow start algorithm used by most
# webservers.
# It attempts to minimize latency, but you may want to increase it so that more
# files are processed.
max_htmlsize = 14_600  # 14.6 kB max size for downloaded html documents
max_filesize = 14_600  # 14.6 kB max filesize for downloaded files


# HTTP Settings
http_useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"  # noqa
