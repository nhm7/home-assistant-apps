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

### RDP security negotiation

`rdp_security` controls the Guacamole security mode and defaults to `any`,
which negotiates a mode supported by both ends. Set it to `nla` for Network
Level Authentication, `tls` for TLS/RDSTLS, or `rdp` for legacy standard RDP
encryption when the target explicitly requires one of those modes. The
`rdp_ignore_cert` option defaults to `false`; leave it disabled whenever the
target certificate can be validated. Enable it only when you intentionally
trust a self-signed or otherwise unverifiable certificate, since it disables
that certificate validation.

These options map to Guacamole's `security` and `ignore-cert` RDP parameters.
See the [Apache Guacamole configuration manual](https://guacamole.apache.org/doc/gug/configuring-guacamole.html#rdp) for the protocol details.

## Local smoke test

The repository includes synthetic options and checks startup, Guacamole
authentication, connection discovery, and the WebSocket tunnel upgrade. From
the repository root, build the image and run it only on localhost:

```sh
docker build -t local/rdp-gateway:0.1.9 apps/rdp-gateway
docker run --rm --name rdp-gateway-test \
  -p 127.0.0.1:18081:8081 \
  -v "$PWD/tests/options.json:/data/options.json:ro" \
  local/rdp-gateway:0.1.9
```

In another terminal, run `python3 tests/smoke.py http://127.0.0.1:18081`.
The WebSocket probe requires `aiohttp` (available in the image):
`docker cp tests/websocket_probe.py rdp-gateway-test:/tmp/` followed by
`docker exec rdp-gateway-test python3 /tmp/websocket_probe.py`. The probe
requires a real RDP server and validates framebuffer data from the joined
tunnel. It is expected to fail when the
synthetic target is unreachable.

### Isolated xrdp fixture

For a disposable, arm64-compatible xrdp target with dummy credentials, build
the fixture and keep both containers on a private Docker network:

```sh
sudo docker build -t local/xrdp-fixture:24.04 tests/xrdp-fixture
sudo docker network create rdp-fixture-net
sudo docker run -d --name xrdp-fixture --network rdp-fixture-net local/xrdp-fixture:24.04
sudo docker run --rm --name rdp-gateway-fixture --network rdp-fixture-net \
  -p 127.0.0.1:18084:8081 \
  -v "$PWD/tests/options-xrdp-fixture.json:/data/options.json:ro" \
  local/rdp-gateway:0.1.9
```

In another terminal, run:

```sh
python3 tests/smoke.py http://127.0.0.1:18084
sudo docker cp tests/websocket_probe.py rdp-gateway-fixture:/tmp/
sudo docker exec rdp-gateway-fixture python3 /tmp/websocket_probe.py
```

The fixture uses
only `fixture` / `fixture-password` and enables `rdp_ignore_cert` solely for
its self-signed test certificate; never reuse those settings for a real host.

After testing, stop the disposable containers and remove their network:

```sh
sudo docker stop rdp-gateway-fixture xrdp-fixture
sudo docker rm xrdp-fixture
sudo docker network rm rdp-fixture-net
```
