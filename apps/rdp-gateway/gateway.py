import base64, hashlib, hmac, json, os, sys, time
from xml.sax.saxutils import escape
from aiohttp import web, ClientSession

OPTIONS = json.load(open("/data/options.json", encoding="utf-8"))
SECRET = OPTIONS["gateway_secret"].encode()
UPSTREAM = "http://127.0.0.1:8080/guacamole"

def configure():
    rdp = OPTIONS
    os.makedirs("/etc/guacamole", exist_ok=True)
    open("/etc/guacamole/guacamole.properties", "w", encoding="utf-8").write("guacd-hostname: 127.0.0.1\nguacd-port: 4822\nhttp-auth-header: REMOTE_USER\n")
    connection = "".join(f"<param name=\"{name}\">{escape(str(value))}</param>" for name, value in (("hostname", rdp["rdp_host"]), ("port", rdp["rdp_port"]), ("username", rdp["rdp_username"]), ("password", rdp["rdp_password"]), ("domain", rdp.get("rdp_domain", ""))))
    open("/etc/guacamole/user-mapping.xml", "w", encoding="utf-8").write(f"<user-mapping><authorize username=\"home-assistant\"><connection name=\"Remote Desktop\"><protocol>rdp</protocol>{connection}</connection></authorize></user-mapping>")

def verify(token):
    try:
        body, signature = token.split(".", 1)
        expected = base64.urlsafe_b64encode(hmac.new(SECRET, body.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
        if not hmac.compare_digest(signature, expected): return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        return payload if payload["exp"] >= time.time() else None
    except (ValueError, KeyError, json.JSONDecodeError): return None

async def launch(request):
    if verify(request.query.get("token", "")) is None: raise web.HTTPForbidden()
    response = web.HTTPFound("./")
    response.set_cookie("rdp_gateway", request.query["token"], httponly=True, samesite="Strict")
    return response

async def proxy(request):
    if verify(request.cookies.get("rdp_gateway", "")) is None: raise web.HTTPForbidden()
    headers = {k:v for k,v in request.headers.items() if k.lower() not in {"host", "cookie"}}
    headers["REMOTE_USER"] = "home-assistant"
    async with request.app["client"].request(request.method, f"{UPSTREAM}{request.rel_url}", headers=headers, data=request.content, allow_redirects=False) as upstream:
        response = web.StreamResponse(status=upstream.status, headers={k:v for k,v in upstream.headers.items() if k.lower() not in {"content-length", "transfer-encoding", "connection", "set-cookie"}})
        for cookie in upstream.headers.getall("Set-Cookie", []): response.headers.add("Set-Cookie", cookie.replace("Path=/guacamole", "Path=/"))
        await response.prepare(request)
        async for chunk in upstream.content.iter_chunked(65536): await response.write(chunk)
        return response

async def start(app): app["client"] = ClientSession()
async def stop(app): await app["client"].close()
if "--configure" in sys.argv: configure(); raise SystemExit(0)
app = web.Application(); app.router.add_get("/launch", launch); app.router.add_route("*", "/{path:.*}", proxy); app.on_startup.append(start); app.on_cleanup.append(stop)
web.run_app(app, port=8081)
