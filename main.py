#!/usr/bin/env python3
"""Publish the finished front page for make.fun news-image-20261124.

The page itself is drawn by ``build/compose.py`` and shipped beside this
file as ``entry.png``.  All this program does is make sure the picture it
is about to hand over is exactly the one that was drawn — it hashes the
file, compares the digest with the value recorded below, and only then
copies it to the grader's output directory.

The output directory comes from ``MAKEFUN_OUTPUT_DIR`` when it is set
(the kit's harness sets it); otherwise it defaults to ``/output``.
Standard library only, no network, no surprises.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path

# Digest of entry.png as rendered by build/compose.py.  Re-run compose.py
# and update this value whenever the artwork changes.
EXPECTED_SHA256 = "ca1b34e4f22f6da9f05e03a56b8abba6c6e18516d20177666b1a123db05da559"

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
DEST_NAME = "entry.png"


def digest_of(path: Path) -> str:
    """SHA-256 of a file, read in blocks so big files stay cheap."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def output_dir() -> Path:
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing: {SOURCE}", file=sys.stderr)
        return 1

    found = digest_of(SOURCE)
    if found != EXPECTED_SHA256:
        print(f"entry.png digest mismatch:\n  expected {EXPECTED_SHA256}\n"
              f"  found    {found}", file=sys.stderr)
        return 1

    target_dir = output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / DEST_NAME
    shutil.copyfile(SOURCE, target)

    if digest_of(target) != EXPECTED_SHA256:
        print(f"copy check failed for {target}", file=sys.stderr)
        return 1

    size = target.stat().st_size
    print(f"ok: {SOURCE} ({size} bytes, sha256 {found}) -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
