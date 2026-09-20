"""Exercise a running gateway without printing credentials or session tokens.

Usage: python3 tests/smoke.py http://127.0.0.1:18081
The gateway must use synthetic test options and be reachable only locally.
"""

import json
import sys
import time
from http.client import RemoteDisconnected
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def run(base: str) -> None:
    base = base.rstrip("/")
    deadline = time.monotonic() + 60
    while True:
        try:
            with urlopen(base + "/", timeout=5) as response:
                html = response.read()
                assert response.status == 200
                assert b"guacamole" in html.lower(), "Expected the Guacamole web application"
            break
        except (URLError, TimeoutError, ConnectionResetError, RemoteDisconnected):
            if time.monotonic() >= deadline:
                raise RuntimeError("Gateway did not become ready within 60 seconds") from None
            time.sleep(1)
    print("PASS: gateway serves Guacamole")

    # A fresh browser sends an empty token request. The gateway must supply
    # configured authentication, without a separate Guacamole login form.
    request = Request(base + "/api/tokens", data=b"", method="POST",
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(request, timeout=10) as response:
        authentication = json.load(response)
    token = authentication.get("authToken")
    assert token, "Automatic authentication did not return a token"
    print("PASS: automatic authentication succeeds")

    providers = authentication.get("availableDataSources", [])
    assert providers, "Authentication did not expose a connection provider"
    connections = []
    for provider in providers:
        url = base + "/api/session/data/" + provider + "/connections?" + urlencode({"token": token})
        with urlopen(url, timeout=10) as response:
            connections.extend(json.load(response).values())
    assert any(item.get("protocol") == "rdp" for item in connections), "No configured RDP connection is available"
    print("PASS: authenticated session exposes an RDP connection")


if __name__ == "__main__":
    try:
        run(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:18081")
    except Exception as error:
        # URL exceptions can contain auth tokens. Report only their type.
        print("FAIL:", type(error).__name__, file=sys.stderr)
        sys.exit(1)
