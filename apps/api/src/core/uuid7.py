"""UUIDv7 generator + datetime UTC helper.

Python 3.14+ has built-in uuid.uuid7() which generates
time-ordered UUIDs (timestamp + random bits).

Provides a cross-version fallback for type checkers and older runtimes.

UUIDv7 is the standard for all primary keys in RapiDrop:
  - Time-ordered → B-tree indexes stay sequential
  - Better INSERT performance vs UUIDv4 (random)
  - Sortable by creation time without an extra column
"""

import os
import time
import uuid
from datetime import UTC, datetime

_has_native_uuid7 = hasattr(uuid, "uuid7")


def _uuid7_fallback() -> uuid.UUID:
    """Manual UUIDv7 implementation as fallback.

    Format (RFC 9562):
      | timestamp_ms (48 bits) | ver (4 bits) | rand_a (12 bits) | var (2 bits) | rand_b (62 bits) |
    """
    timestamp_ms = int(time.time() * 1000)
    rand_bytes = os.urandom(10)

    # Build 16 bytes: 6 timestamp + 10 random
    raw = bytearray(16)

    # Bytes 0-5: 48-bit Unix timestamp in milliseconds (big-endian)
    raw[0] = (timestamp_ms >> 40) & 0xFF
    raw[1] = (timestamp_ms >> 32) & 0xFF
    raw[2] = (timestamp_ms >> 24) & 0xFF
    raw[3] = (timestamp_ms >> 16) & 0xFF
    raw[4] = (timestamp_ms >> 8) & 0xFF
    raw[5] = timestamp_ms & 0xFF

    # Bytes 6-7: high 2 bytes of random + version nibble
    raw[6] = (rand_bytes[0] & 0x0F) | 0x70   # version 7
    raw[7] = rand_bytes[1]

    # Byte 8: variant (10xx)
    raw[8] = (rand_bytes[2] & 0x3F) | 0x80

    # Bytes 9-15: remaining random bytes
    raw[9] = rand_bytes[3]
    raw[10] = rand_bytes[4]
    raw[11] = rand_bytes[5]
    raw[12] = rand_bytes[6]
    raw[13] = rand_bytes[7]
    raw[14] = rand_bytes[8]
    raw[15] = rand_bytes[9]

    return uuid.UUID(bytes=bytes(raw), version=7)


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7 (time-ordered) identifier.

    Uses Python 3.14+'s built-in uuid.uuid7() when available,
    with a manual fallback for older runtimes or type checkers.
    """
    if _has_native_uuid7:
        return uuid.uuid7()  # type: ignore  # Pyright: stubs don't include uuid7 (Python 3.14+)
    return _uuid7_fallback()


def utcnow() -> datetime:
    """Return current UTC time as a naive datetime.

    Replacement for deprecated datetime.utcnow().
    Returns a naive datetime (tzinfo=None) so SQLAlchemy DateTime
    columns without timezone=True continue to work.
    """
    return datetime.now(UTC).replace(tzinfo=None)
