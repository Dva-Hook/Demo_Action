#!/usr/bin/env python3
"""Resolve an OTA catalog selection to a downloadable package URL."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://roms.danielspringer.at"


class ResolverError(RuntimeError):
    pass


class _OtaPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.catalog: dict[str, dict[str, list[str]]] | None = None
        self.ota_key = ""
        self.csrf = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "select" and attributes.get("id") == "device":
            raw_catalog = attributes.get("data-devices")
            if raw_catalog:
                try:
                    catalog = json.loads(raw_catalog)
                except json.JSONDecodeError as error:
                    raise ResolverError(f"invalid device catalog JSON: {error}") from error
                if isinstance(catalog, dict):
                    self.catalog = catalog
        elif attributes.get("id") == "resultBox":
            self.ota_key = attributes.get("data-ota-key") or ""
            self.csrf = attributes.get("data-csrf") or ""


def _parse_page(html: str) -> _OtaPageParser:
    parser = _OtaPageParser()
    parser.feed(html)
    return parser


def _match_key(values: dict[str, Any], requested: str, label: str) -> str:
    match = next((value for value in values if value.casefold() == requested.casefold()), None)
    if match is None:
        available = ", ".join(values)
        raise ResolverError(f"unknown {label} {requested}; available: {available}")
    return match


def _save_debug(debug_dir: Path | None, name: str, content: str) -> None:
    if debug_dir is None:
        return
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / name).write_text(content, encoding="utf-8")


def resolve_ota(
    client: Any,
    device: str,
    region: str,
    version_index: int,
    base_url: str = DEFAULT_BASE_URL,
    debug_dir: Path | None = None,
) -> dict[str, Any]:
    if version_index < 0:
        raise ResolverError("version index must be zero or greater")

    base_url = base_url.rstrip("/")
    page_url = f"{base_url}/index.php?view=ota"

    catalog_response = client.get(page_url)
    catalog_response.raise_for_status()
    _save_debug(debug_dir, "01-catalog.html", catalog_response.text)
    catalog = _parse_page(catalog_response.text).catalog
    if not catalog:
        raise ResolverError("the OTA page did not contain a device catalog")

    selected_device = _match_key(catalog, device, "device")
    regions = catalog[selected_device]
    selected_region = _match_key(regions, region, "region")
    versions = regions[selected_region]
    if version_index >= len(versions):
        raise ResolverError(
            f"version index {version_index} is out of range for "
            f"{selected_device}/{selected_region} ({len(versions)} versions)"
        )
    version = versions[version_index]

    selection_response = client.post(
        page_url,
        data={
            "device": selected_device,
            "region": selected_region,
            "version": str(version_index),
        },
    )
    selection_response.raise_for_status()
    _save_debug(debug_dir, "02-selection.html", selection_response.text)
    selection = _parse_page(selection_response.text)
    if not selection.ota_key or not selection.csrf:
        raise ResolverError("the OTA selection page did not contain resolver tokens")

    resolve_response = client.post(
        f"{page_url}&ota_action=resolve_json",
        files={
            "k": (None, selection.ota_key),
            "csrf": (None, selection.csrf),
        },
    )
    resolve_response.raise_for_status()
    try:
        payload = resolve_response.json()
    except (TypeError, ValueError) as error:
        raise ResolverError("the OTA resolver returned invalid JSON") from error
    _save_debug(
        debug_dir,
        "03-resolve.json",
        json.dumps(payload, ensure_ascii=False, indent=2),
    )
    if not isinstance(payload, dict) or not payload.get("ok"):
        message = payload.get("message") if isinstance(payload, dict) else None
        raise ResolverError(message or "the OTA resolver rejected the selection")
    ota_url = str(payload.get("url") or "").strip()
    if not ota_url:
        raise ResolverError("the OTA resolver returned no OTA URL")

    return {
        "device": selected_device,
        "region": selected_region,
        "version": version,
        "version_index": version_index,
        "ota_url": ota_url,
        "manual": bool(payload.get("manual")),
    }


def _write_github_output(path: Path, result: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(f"ota_url={result['ota_url']}\n")
        output.write(f"version={result['version']}\n")
        output.write(f"device={result['device']}\n")
        output.write(f"region={result['region']}\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--version-index", type=int, default=0)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--debug-dir", type=Path)
    parser.add_argument("--github-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        import httpx

        with httpx.Client(
            follow_redirects=True,
            timeout=httpx.Timeout(60.0, connect=20.0),
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "Chrome/131.0 Safari/537.36"
                )
            },
        ) as client:
            result = resolve_ota(
                client,
                args.device,
                args.region,
                args.version_index,
                args.base_url,
                args.debug_dir,
            )
        if args.github_output:
            _write_github_output(args.github_output, result)
        print(f"Resolved {result['device']} {result['region']}: {result['version']}")
        print(result["ota_url"])
        return 0
    except Exception as error:
        print(f"::error::OTA resolver failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
