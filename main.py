#!/usr/bin/env python3
"""Publish the finished front page for the make.fun news-image-20261124 entry.

The artwork itself (entry.png) is produced separately by the builder script
and shipped next to this file.  This runner has exactly one job: prove the
bundled image is the exact file the entry was graded on, then place an
identical copy where the harness expects it.

It is deliberately boring: standard library only, no network, no clock,
no randomness, so the same input always yields the same output.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

# SHA-256 of the front-page image this entry was built from.  If the image
# on disk does not hash to this value, something changed it and we refuse
# to publish it rather than silently shipping the wrong picture.
EXPECTED_DIGEST = (
    "ca1b34e4f22f6da9f05e03a56b8abba6c6e18516d20177666b1a123db05da559"
)

IMAGE_NAME = "entry.png"

# Where the copy lands when MAKEFUN_OUTPUT_DIR is not set.
FALLBACK_OUTPUT_DIR = "/output"


def folder_of_this_file() -> Path:
    """Directory holding this script (and, by convention, entry.png)."""
    return Path(__file__).resolve().parent


def digest_of(path: Path) -> str:
    """SHA-256 hex digest of a file, read in modest chunks."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def read_verified_image() -> bytes:
    """Return the bytes of entry.png, but only if its hash matches.

    Raises:
        FileNotFoundError: no entry.png sits next to this script.
        ValueError: the image exists but is not the expected one.
    """
    image_path = folder_of_this_file() / IMAGE_NAME
    if not image_path.is_file():
        raise FileNotFoundError(
            f"expected image not found: {image_path} "
            f"(run the builder first so entry.png sits next to main.py)"
        )
    actual = digest_of(image_path)
    if actual != EXPECTED_DIGEST:
        raise ValueError(
            f"entry.png failed its integrity check: "
            f"expected sha256 {EXPECTED_DIGEST}, got {actual}. "
            f"The image on disk is not the one this entry was built from."
        )
    return image_path.read_bytes()


def destination_dir() -> Path:
    """Output folder from the environment, falling back to /output."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return Path(raw) if raw else Path(FALLBACK_OUTPUT_DIR)


def publish(image_bytes: bytes, out_dir: Path) -> Path:
    """Write the verified bytes to <out_dir>/entry.png and return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / IMAGE_NAME
    target.write_bytes(image_bytes)
    return target


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    try:
        image_bytes = read_verified_image()
    except (FileNotFoundError, ValueError) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return 1
    except OSError as problem:
        print(f"error: could not read entry.png: {problem}", file=sys.stderr)
        return 1

    if not image_bytes:
        print("error: entry.png is empty, refusing to publish it",
              file=sys.stderr)
        return 1

    if check_only:
        # Verify-only mode: prove the bundled image is intact without
        # writing anything, for a quick pre-flight before a real run.
        print(
            f"ok: entry.png verified "
            f"({len(image_bytes)} bytes, sha256 {EXPECTED_DIGEST})"
        )
        return 0

    try:
        target = publish(image_bytes, destination_dir())
    except OSError as problem:
        print(f"error: could not write output: {problem}", file=sys.stderr)
        return 1

    print(
        f"wrote {target} ({len(image_bytes)} bytes, "
        f"sha256 {digest_of(target)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
