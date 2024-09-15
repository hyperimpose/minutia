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

import asyncio
import argparse


if __name__ == "__main__":
    # Create the command line argument parser
    parser = argparse.ArgumentParser(prog="minutia")
    subparsers = parser.add_subparsers(required=True, dest="command")
    # explicit
    exp_p = subparsers.add_parser("explicit", help="Start the explicit server")
    exp_p.add_argument('-u', '--unix', help='Use a unix socket at path')
    exp_p.add_argument('-d', '--debug',
                       action='store_true',
                       help='Enable debugging')

    args = parser.parse_args()

    match args.command:
        case "explicit":
            if not (args.unix):
                parser.error("No protocol specified: -u/--unix")

            from services.explicit import unix_server
            asyncio.run(unix_server.init(args.unix, debug=args.debug))
