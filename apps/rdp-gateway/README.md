# RDP Gateway App

This app bundles Apache Guacamole as an HTML5 RDP gateway.

## Security

- `rdp_password` is a password field. Never expose it
  in logs, commits, or URLs.
- Permit RDP port 3389 only between the app and target machine; never expose it
  directly to the internet.
- By default, the sidebar panel is restricted to Home Assistant administrators.
  Set `panel_admin: false` in `config.yaml` only when every signed-in user
  should be allowed to open it.

The app generates Guacamole's RDP connection configuration at startup. Home
Assistant Ingress authenticates users before requests reach the app.

## Local smoke test

The repository includes synthetic options and checks startup, Guacamole
authentication, connection discovery, and the WebSocket tunnel upgrade. From
the repository root, build the image and run it only on localhost:

```sh
docker build -t local/rdp-gateway:0.1.8 apps/rdp-gateway
docker run --rm --name rdp-gateway-test \
  -p 127.0.0.1:18081:8081 \
  -v "$PWD/tests/options.json:/data/options.json:ro" \
  local/rdp-gateway:0.1.8
```

In another terminal, run `python3 tests/smoke.py http://127.0.0.1:18081`.
The WebSocket probe requires `aiohttp` (available in the image):
`docker cp tests/websocket_probe.py rdp-gateway-test:/tmp/` followed by
`docker exec rdp-gateway-test python3 /tmp/websocket_probe.py`. The probe
does not establish a real desktop session; an RDP server fixture is required
to validate the final framebuffer connection.
