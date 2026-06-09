"""UUIDv7 generator.

Python 3.14+ has built-in uuid.uuid7() which generates
time-ordered UUIDs (timestamp + random bits).

UUIDv7 is the standard for all primary keys in RapiDrop:
  - Time-ordered → B-tree indexes stay sequential
  - Better INSERT performance vs UUIDv4 (random)
  - Sortable by creation time without an extra column
"""

import uuid


def uuid7() -> uuid.UUID:
    """Generate a UUIDv7 (time-ordered) identifier.

    Uses Python 3.14+'s built-in uuid.uuid7().
    """
    return uuid.uuid7()
