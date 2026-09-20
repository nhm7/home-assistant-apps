"""Ingress-only reverse proxy for the bundled Guacamole web application."""
import base64
import hashlib
import hmac
import json
import os
import subprocess
import sys
from urllib.parse import urlencode
from xml.sax.saxutils import escape

from aiohttp import ClientSession, web

OPTIONS = json.load(open("/data/options.json", encoding="utf-8"))
UPSTREAM = "http://127.0.0.1:8080/guacamole"
JSON_KEY = hashlib.md5(OPTIONS["rdp_password"].encode()).hexdigest()


def configure() -> None:
    os.makedirs("/etc/guacamole", exist_ok=True)
    with open("/etc/guacamole/guacamole.properties", "w", encoding="utf-8") as file:
        file.write(f"guacd-hostname: 127.0.0.1\nguacd-port: 4822\njson-secret-key: {JSON_KEY}\n")


def connection_data() -> str:
    parameters = {"hostname": OPTIONS["rdp_host"], "port": str(OPTIONS["rdp_port"]), "username": OPTIONS["rdp_username"], "password": OPTIONS["rdp_password"], "domain": OPTIONS.get("rdp_domain", "")}
    payload = json.dumps({"username": "home-assistant", "expires": int((__import__("time").time() + 60) * 1000), "connections": {"rdp": {"name": "Remote Desktop", "protocol": "rdp", "parameters": parameters}}}, separators=(",", ":")).encode()
    signed = hmac.new(bytes.fromhex(JSON_KEY), payload, hashlib.sha256).digest() + payload
    encrypted = subprocess.run(["openssl", "enc", "-aes-128-cbc", "-K", JSON_KEY, "-iv", "00000000000000000000000000000000", "-nosalt"], input=signed, capture_output=True, check=True).stdout
    return base64.b64encode(encrypted).decode()


async def proxy(request: web.Request) -> web.StreamResponse:
    if request.path == "/" and "data" not in request.query:
        # Keep the redirect relative so Home Assistant Ingress retains its
        # app-specific URL prefix instead of navigating to the HA dashboard.
        raise web.HTTPFound("?" + urlencode({"data": connection_data()}))
    headers = {key: value for key, value in request.headers.items() if key.lower() not in {"host", "cookie"}}
    async with request.app["client"].request(request.method, f"{UPSTREAM}{request.rel_url}", headers=headers, data=request.content, allow_redirects=False) as upstream:
        response = web.StreamResponse(status=upstream.status, headers={key: value for key, value in upstream.headers.items() if key.lower() not in {"content-length", "transfer-encoding", "connection", "set-cookie"}})
        for cookie in upstream.headers.getall("Set-Cookie", []):
            response.headers.add("Set-Cookie", cookie.replace("Path=/guacamole", "Path=/"))
        await response.prepare(request)
        async for chunk in upstream.content.iter_chunked(65536):
            await response.write(chunk)
        return response


async def start(app: web.Application) -> None:
    app["client"] = ClientSession()


async def stop(app: web.Application) -> None:
    await app["client"].close()


if "--configure" in sys.argv:
    configure()
    raise SystemExit(0)

app = web.Application()
app.router.add_route("*", "/{path:.*}", proxy)
app.on_startup.append(start)
app.on_cleanup.append(stop)
web.run_app(app, port=8081)
