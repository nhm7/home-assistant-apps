"""Ingress-only reverse proxy for the bundled Guacamole web application."""
import json
import os
import sys
from xml.sax.saxutils import escape

from aiohttp import ClientSession, web

OPTIONS = json.load(open("/data/options.json", encoding="utf-8"))
UPSTREAM = "http://127.0.0.1:8080/guacamole"


def configure() -> None:
    os.makedirs("/etc/guacamole", exist_ok=True)
    with open("/etc/guacamole/guacamole.properties", "w", encoding="utf-8") as file:
        file.write("guacd-hostname: 127.0.0.1\nguacd-port: 4822\nhttp-auth-header: REMOTE_USER\n")
    parameters = (("hostname", OPTIONS["rdp_host"]), ("port", OPTIONS["rdp_port"]), ("username", OPTIONS["rdp_username"]), ("password", OPTIONS["rdp_password"]), ("domain", OPTIONS.get("rdp_domain", "")))
    values = "".join(f'<param name="{name}">{escape(str(value))}</param>' for name, value in parameters)
    with open("/etc/guacamole/user-mapping.xml", "w", encoding="utf-8") as file:
        file.write(f'<user-mapping><authorize username="home-assistant"><connection name="Remote Desktop"><protocol>rdp</protocol>{values}</connection></authorize></user-mapping>')


async def proxy(request: web.Request) -> web.StreamResponse:
    headers = {key: value for key, value in request.headers.items() if key.lower() not in {"host", "cookie"}}
    headers["REMOTE_USER"] = "home-assistant"
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
