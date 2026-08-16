#!/usr/bin/env python3
"""Extract the Linux version and build time from an Android boot image."""

from __future__ import annotations

import argparse
import gzip
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any


BOOT_MAGIC = b"ANDROID!"
VERSION_RE = re.compile(rb"Linux version ([^\s\x00]+)[^\x00\r\n]{0,1024}")
BUILD_TIME_RE = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) "
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) +"
    r"\d{1,2} \d{2}:\d{2}:\d{2} (?:[A-Za-z0-9+:-]+ )?\d{4}"
)


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _kernel_blob(image: bytes) -> bytes:
    if len(image) < 44 or not image.startswith(BOOT_MAGIC):
        return image

    kernel_size = _u32(image, 8)
    header_version = _u32(image, 40)
    if header_version in (3, 4):
        kernel_offset = 4096
    else:
        page_size = _u32(image, 36)
        if page_size < 512 or page_size > 65536 or page_size & (page_size - 1):
            return image
        kernel_offset = page_size

    kernel_end = kernel_offset + kernel_size
    if kernel_size == 0 or kernel_end > len(image):
        return image
    return image[kernel_offset:kernel_end]


def _external_decompress(data: bytes, executable: str) -> bytes | None:
    command = shutil.which(executable)
    if not command:
        return None
    try:
        completed = subprocess.run(
            [command, "-dc"],
            input=data,
            capture_output=True,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return completed.stdout if completed.returncode == 0 and completed.stdout else None


def _candidates(kernel: bytes):
    yield kernel
    if kernel.startswith(b"\x1f\x8b"):
        try:
            yield gzip.decompress(kernel)
        except (EOFError, OSError):
            pass
    if kernel.startswith((b"\x02\x21\x4c\x18", b"\x04\x22\x4d\x18")):
        decompressed = _external_decompress(kernel, "lz4")
        if decompressed:
            yield decompressed
    if kernel.startswith(b"\x28\xb5\x2f\xfd"):
        decompressed = _external_decompress(kernel, "zstd")
        if decompressed:
            yield decompressed


def _scan_version(data: bytes) -> dict[str, Any] | None:
    match = VERSION_RE.search(data)
    if not match:
        return None
    line = match.group(0).decode("utf-8", errors="replace").strip()
    build_time = BUILD_TIME_RE.search(line)
    return {
        "found": True,
        "kernel_version": match.group(1).decode("ascii", errors="replace"),
        "kernel_time": build_time.group(0) if build_time else "Unknown",
        "version_line": line,
    }


def extract_kernel_info(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    kernel = _kernel_blob(image)
    for candidate in _candidates(kernel):
        result = _scan_version(candidate)
        if result:
            return result
    return {
        "found": False,
        "kernel_version": "Unknown",
        "kernel_time": "Unknown",
        "version_line": "",
    }


def _write_github_output(path: Path, result: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(f"found={'true' if result['found'] else 'false'}\n")
        output.write(f"kernel_version={result['kernel_version']}\n")
        output.write(f"kernel_time={result['kernel_time']}\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--github-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        result = extract_kernel_info(args.image)
        if args.github_output:
            _write_github_output(args.github_output, result)
        if result["found"]:
            print(result["version_line"])
        else:
            print("::warning::Linux version string was not found in boot.img")
        return 0
    except Exception as error:
        print(f"::error::Kernel info extraction failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
