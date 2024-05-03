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

import logging
import os


# ====================================================================
# Erlang
# ====================================================================

# Erlang Port Settings
FD_IN = 0
FD_OUT = 1


# Readers ============================================================

async def read_packet(loop) -> bytes:
    return await loop.run_in_executor(None, _read_packet)


def _read_packet() -> bytes | None:
    length_b = os.read(0, 2)
    if len(length_b) != 2:  # We configure the erlang port with {packet, 2}
        return None  # The port closed

    length = int.from_bytes(length_b, "big")

    packet = os.read(FD_IN, length)
    assert len(packet) == length

    return packet


# Writers ============================================================

def write_data(packet: bytes):
    packet_len = len(packet).to_bytes(2, "big")
    os.write(FD_OUT, packet_len)
    os.write(FD_OUT, packet)


def send(term):
    write_data(bencode(term))


def log(level, term):
    send(("log", level, term))


# Helpers ============================================================

def bencode(term):
    """
    Simple recursive bencode encoder.

    - Because the data in libminutia are not deeply nested, it is unlikely that
      we will hit the recursion limit.
    - Booleans are converted to the strings 'true' and 'false'.
    - None is converted to the empty string.
    """
    if term is False:
        return b"5:false"
    if term is True:
        return b"4:true"
    if term is None:
        return b"0:"
    if isinstance(term, int):
        return b"i" + str(term).encode() + b"e"
    if isinstance(term, float):
        return bencode(str(term).encode())
    if isinstance(term, str):
        return bencode(term.encode())
    if isinstance(term, bytes):
        return str(len(term)).encode() + b":" + term
    if isinstance(term, list) or isinstance(term, tuple):
        return b"l" + b"".join([bencode(x) for x in term]) + b"e"
    if isinstance(term, dict):  # in Python 3.6+ dicts are ordered
        acc = b"d"
        for k, v in term.items():
            if not isinstance(k, str) and not isinstance(k, bytes):
                raise ValueError("Dict keys must be of type str or bytes")
            acc += bencode(k)
            acc += bencode(v)
        acc += b"e"
        return acc

    raise TypeError(f"Unexpect term {term} of type {type(term)}")


# ====================================================================
# Logging
# ====================================================================

class ErlangLogHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)

    def emit(self, record):
        log(record.levelname.lower(), self.format(record))
