#!/usr/bin/env python3
"""Extract module version requirements and compare them with Module.symvers."""

from __future__ import annotations

import argparse
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class KmiError(RuntimeError):
    """Raised for malformed KMI inputs."""


@dataclass(frozen=True)
class KmiReport:
    checked: int
    checked_external: int
    missing: list[str]
    mismatches: list[str]

    @property
    def ok(self) -> bool:
        return not self.missing and not self.mismatches


def _parse_crc(value: str | int) -> int:
    if isinstance(value, int):
        if 0 <= value <= 0xFFFFFFFFFFFFFFFF:
            return value
        raise KmiError(f"CRC integer out of range: {value}")
    if not isinstance(value, str):
        raise KmiError(f"CRC must be a string or integer, got {type(value).__name__}")
    try:
        parsed = int(value, 0)
    except ValueError as exc:
        raise KmiError(f"invalid CRC {value!r}") from exc
    if not 0 <= parsed <= 0xFFFFFFFFFFFFFFFF:
        raise KmiError(f"CRC out of range: {value!r}")
    return parsed


def parse_module_symvers(path: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    for line_number, raw_line in enumerate(
        Path(path).read_text(encoding="utf-8", errors="strict").splitlines(), 1
    ):
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) < 3:
            raise KmiError(f"{path}:{line_number}: expected at least 3 columns")
        crc = _parse_crc(fields[0])
        symbol = fields[1]
        previous = symbols.get(symbol)
        if previous is not None and previous != crc:
            raise KmiError(
                f"{path}:{line_number}: conflicting CRC for {symbol}: "
                f"0x{previous:08x} vs 0x{crc:08x}"
            )
        symbols[symbol] = crc
    if not symbols:
        raise KmiError(f"{path}: no symbols found")
    return symbols


def _plausible_name(raw: bytes) -> str | None:
    name_bytes = raw.split(b"\0", 1)[0]
    if not name_bytes:
        return None
    try:
        name = name_bytes.decode("ascii")
    except UnicodeDecodeError:
        return None
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_."
    if any(character not in allowed for character in name):
        return None
    return name


def parse_module_versions(path: Path) -> dict[str, int]:
    try:
        from elftools.elf.elffile import ELFFile
    except ImportError as exc:
        raise KmiError("pyelftools is required to extract module __versions") from exc

    with Path(path).open("rb") as stream:
        elf = ELFFile(stream)
        section = elf.get_section_by_name("__versions")
        if section is None:
            raise KmiError(f"{path}: ELF has no __versions section")
        data = section.data()
        word_size = elf.elfclass // 8
        endian = "<" if elf.little_endian else ">"
        candidates = (64, 60) if word_size == 8 else (60, 64)
        entry_size = next(
            (
                size
                for size in candidates
                if len(data) % size == 0
                and all(
                    _plausible_name(data[offset + word_size : offset + size])
                    for offset in range(0, len(data), size)
                )
            ),
            None,
        )
        if entry_size is None:
            raise KmiError(
                f"{path}: unsupported __versions layout, size={len(data)} "
                f"elfclass={elf.elfclass}"
            )
        unpack = endian + ("Q" if word_size == 8 else "I")
        versions: dict[str, int] = {}
        for offset in range(0, len(data), entry_size):
            crc = struct.unpack_from(unpack, data, offset)[0]
            name = _plausible_name(data[offset + word_size : offset + entry_size])
            if name is None:
                raise KmiError(f"{path}: malformed symbol at __versions+0x{offset:x}")
            previous = versions.get(name)
            if previous is not None and previous != crc:
                raise KmiError(f"{path}: conflicting CRC entries for {name}")
            versions[name] = crc
        return versions


def compare_versions(
    actual: dict[str, int],
    expected_modules: dict[str, dict[str, int]],
    external_symbols: dict[str, int],
) -> KmiReport:
    checked = 0
    checked_external = 0
    missing: list[str] = []
    mismatches: list[str] = []
    for module_name in sorted(expected_modules):
        for symbol in sorted(expected_modules[module_name]):
            expected_crc = expected_modules[module_name][symbol]
            key = f"{module_name}:{symbol}"
            if symbol in actual:
                checked += 1
                actual_crc = actual[symbol]
                if actual_crc != expected_crc:
                    mismatches.append(
                        f"{key}: expected 0x{expected_crc:08x}, "
                        f"got 0x{actual_crc:08x}"
                    )
            elif symbol in external_symbols:
                checked_external += 1
                external_crc = external_symbols[symbol]
                if external_crc != expected_crc:
                    mismatches.append(
                        f"{key}: external expected 0x{expected_crc:08x}, "
                        f"got 0x{external_crc:08x}"
                    )
            else:
                missing.append(key)
    return KmiReport(checked, checked_external, missing, mismatches)


def _format_crc_map(symbols: dict[str, int]) -> dict[str, str]:
    return {symbol: f"0x{crc:08x}" for symbol, crc in sorted(symbols.items())}


def write_reference(
    output: Path,
    module_paths: Iterable[Path],
    external_symbols: dict[str, int],
) -> None:
    modules: dict[str, dict[str, str]] = {}
    for module_path in module_paths:
        name = Path(module_path).name
        if name in modules:
            raise KmiError(f"duplicate module basename: {name}")
        modules[name] = _format_crc_map(parse_module_versions(module_path))
    document = {
        "schema_version": 1,
        "modules": modules,
        "external_symbols": _format_crc_map(external_symbols),
    }
    Path(output).write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_reference(path: Path) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KmiError(f"cannot read reference {path}: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise KmiError("reference schema_version must be 1")
    raw_modules = document.get("modules")
    raw_external = document.get("external_symbols", {})
    if not isinstance(raw_modules, dict) or not isinstance(raw_external, dict):
        raise KmiError("reference modules/external_symbols must be objects")
    modules: dict[str, dict[str, int]] = {}
    for module, raw_symbols in raw_modules.items():
        if not isinstance(module, str) or not isinstance(raw_symbols, dict):
            raise KmiError("reference module entries must be symbol objects")
        modules[module] = {
            symbol: _parse_crc(crc) for symbol, crc in raw_symbols.items()
        }
    external = {symbol: _parse_crc(crc) for symbol, crc in raw_external.items()}
    return modules, external


def _parse_external(values: list[str]) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise KmiError(f"external symbol must be NAME=CRC: {value!r}")
        name, crc = value.split("=", 1)
        if not name:
            raise KmiError(f"external symbol name is empty: {value!r}")
        parsed[name] = _parse_crc(crc)
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract")
    extract_parser.add_argument("modules", nargs="+", type=Path)
    extract_parser.add_argument("--output", required=True, type=Path)
    extract_parser.add_argument("--external", action="append", default=[])

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--symvers", required=True, type=Path)
    check_parser.add_argument("--reference", required=True, type=Path)

    args = parser.parse_args()
    try:
        if args.command == "extract":
            write_reference(args.output, args.modules, _parse_external(args.external))
            print(f"KMI_REFERENCE_OK modules={len(args.modules)} output={args.output}")
            return 0
        actual = parse_module_symvers(args.symvers)
        modules, external = load_reference(args.reference)
        report = compare_versions(actual, modules, external)
    except (KmiError, OSError) as exc:
        print(f"KMI_INPUT_ERROR {exc}")
        return 2

    for mismatch in report.mismatches:
        print(f"KMI_CRC_MISMATCH {mismatch}")
    for missing in report.missing:
        print(f"KMI_MISSING {missing}")
    if not report.ok:
        print(
            f"KMI_FAIL checked={report.checked} external={report.checked_external} "
            f"mismatch={len(report.mismatches)} missing={len(report.missing)}"
        )
        return 1
    print(
        f"KMI_OK checked={report.checked} external={report.checked_external} "
        "mismatch=0 missing=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
