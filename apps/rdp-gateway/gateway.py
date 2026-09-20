"""Ingress-only reverse proxy for the bundled Guacamole web application."""
import base64
import asyncio
import hashlib
import hmac
import json
import os
import subprocess
import sys
import secrets
from pathlib import Path
from urllib.parse import urlencode
from xml.sax.saxutils import escape

from aiohttp import ClientSession, ClientTimeout, WSMsgType, web

OPTIONS = json.load(open("/data/options.json", encoding="utf-8"))
UPSTREAM = "http://127.0.0.1:8080/guacamole"
KEY_PATH = Path("/tmp/rdp-json-key")


def configure() -> None:
    KEY_PATH.write_text(secrets.token_hex(16))
    KEY_PATH.chmod(0o600)
    os.makedirs("/etc/guacamole", exist_ok=True)
    with open("/etc/guacamole/guacamole.properties", "w", encoding="utf-8") as file:
        file.write(f"guacd-hostname: 127.0.0.1\nguacd-port: 4822\njson-secret-key: {KEY_PATH.read_text()}\n")


def connection_data() -> str:
    JSON_KEY = KEY_PATH.read_text()
    parameters = {"hostname": OPTIONS["rdp_host"], "port": str(OPTIONS["rdp_port"]), "username": OPTIONS["rdp_username"], "password": OPTIONS["rdp_password"], "domain": OPTIONS.get("rdp_domain", "")}
    # The JSON extension's connection schema has no ``name`` field; the map
    # key is used as the connection identifier/display name by Guacamole.
    payload = json.dumps({"username": "home-assistant", "expires": int((__import__("time").time() + 60) * 1000), "connections": {"rdp": {"protocol": "rdp", "parameters": parameters}}}, separators=(",", ":")).encode()
    signed = hmac.new(bytes.fromhex(JSON_KEY), payload, hashlib.sha256).digest() + payload
    encrypted = subprocess.run(["openssl", "enc", "-aes-128-cbc", "-K", JSON_KEY, "-iv", "00000000000000000000000000000000", "-nosalt"], input=signed, capture_output=True, check=True).stdout
    return base64.b64encode(encrypted).decode()


async def proxy(request: web.Request) -> web.StreamResponse:
    headers = {key: value for key, value in request.headers.items() if key.lower() not in {"host", "cookie", "connection", "upgrade", "content-length", "transfer-encoding", "sec-websocket-key", "sec-websocket-version", "sec-websocket-extensions", "sec-websocket-protocol"}}
    target = f"{UPSTREAM}{request.rel_url}"
    if request.headers.get("Upgrade", "").lower() == "websocket":
        async with request.app["client"].ws_connect(target, headers=headers, protocols=("guacamole",), max_msg_size=0) as upstream:
            downstream = web.WebSocketResponse(protocols=("guacamole",), max_msg_size=0)
            await downstream.prepare(request)
            async def relay(source, destination):
                async for message in source:
                    if message.type == WSMsgType.TEXT:
                        await destination.send_str(message.data)
                    elif message.type == WSMsgType.BINARY:
                        await destination.send_bytes(message.data)
                    else:
                        break
            tasks = [asyncio.create_task(relay(downstream, upstream)), asyncio.create_task(relay(upstream, downstream))]
            try:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                await downstream.close()
            return downstream
    # Do not forward an empty request stream on bodyless methods.  aiohttp
    # otherwise emits a chunked GET, which Guacamole rejects as unsupported
    # media type on its connection-list endpoint.
    body = request.content if request.method not in {"GET", "HEAD"} else None
    if request.path == "/api/tokens" and request.method == "POST":
        # Ingress authenticates the browser. Issue fresh credentials internally,
        # so no expiring bootstrap token needs to survive a browser redirect.
        body = {"data": await asyncio.to_thread(connection_data)}
        headers.pop("Content-Type", None)
    async with request.app["client"].request(request.method, target, headers=headers, data=body, allow_redirects=False) as upstream:
        response = web.StreamResponse(status=upstream.status, headers={key: value for key, value in upstream.headers.items() if key.lower() not in {"content-length", "transfer-encoding", "connection", "set-cookie"}})
        for cookie in upstream.headers.getall("Set-Cookie", []):
            response.headers.add("Set-Cookie", cookie.replace("Path=/guacamole", "Path=/"))
        await response.prepare(request)
        async for chunk in upstream.content.iter_chunked(65536):
            await response.write(chunk)
        return response


async def start(app: web.Application) -> None:
    app["client"] = ClientSession(auto_decompress=False, timeout=ClientTimeout(total=None, sock_connect=10))


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
