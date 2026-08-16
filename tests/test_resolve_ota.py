import json
import unittest

from tools.resolve_ota import ResolverError, resolve_ota


CATALOG_HTML = """
<select id="device" data-devices='{&quot;OP 13&quot;:{&quot;CN&quot;:[&quot;PJZ110_16.0.10.501(CN01)&quot;,&quot;PJZ110_16.0.9.402(CN01)&quot;]}}'>
</select>
"""

SELECTION_HTML = """
<div id="resultBox"
     data-ota-key="ota-key-123"
     data-csrf="csrf-456">
</div>
"""


class FakeResponse:
    def __init__(self, *, text="", payload=None, status_code=200):
        self.text = text
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self):
        self.calls = []

    def get(self, url):
        self.calls.append(("GET", url, None))
        return FakeResponse(text=CATALOG_HTML)

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if "ota_action=resolve_json" in url:
            return FakeResponse(
                payload={
                    "ok": True,
                    "url": "https://cdn.example/ota.zip?sign=temporary",
                    "manual": False,
                }
            )
        return FakeResponse(text=SELECTION_HTML)


class ResolveOtaTests(unittest.TestCase):
    def test_resolves_selected_version_through_site_session(self):
        client = FakeClient()

        result = resolve_ota(client, "OP 13", "CN", 1, "https://roms.example")

        self.assertEqual(result["version"], "PJZ110_16.0.9.402(CN01)")
        self.assertEqual(result["ota_url"], "https://cdn.example/ota.zip?sign=temporary")
        self.assertEqual(client.calls[1][2]["data"]["version"], "1")
        multipart = client.calls[2][2]["files"]
        self.assertEqual(multipart["k"], (None, "ota-key-123"))
        self.assertEqual(multipart["csrf"], (None, "csrf-456"))

    def test_rejects_unknown_region_before_selection_request(self):
        client = FakeClient()

        with self.assertRaisesRegex(ResolverError, "region JP"):
            resolve_ota(client, "OP 13", "JP", 0, "https://roms.example")

        self.assertEqual(len(client.calls), 1)

    def test_rejects_resolver_response_without_url(self):
        class EmptyUrlClient(FakeClient):
            def post(self, url, **kwargs):
                if "ota_action=resolve_json" in url:
                    return FakeResponse(payload={"ok": True, "url": ""})
                return super().post(url, **kwargs)

        with self.assertRaisesRegex(ResolverError, "no OTA URL"):
            resolve_ota(EmptyUrlClient(), "OP 13", "CN", 0, "https://roms.example")


if __name__ == "__main__":
    unittest.main()
