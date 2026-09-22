# Repository notes

Testing instructions: [docs/testing.md](docs/testing.md).

- RDP Gateway settings are translated through `apps/rdp-gateway/translations/en.yaml`;
  keep every `config.yaml` schema key covered by an English name and description.
- The app starts Guacamole and Tomcat before the ingress proxy. A healthy HTTP
  smoke test proves startup and authentication, not connectivity to a real RDP target.
- Do not weaken certificate validation to diagnose a refused RDP connection;
  identify the target host and inspect its network/server logs first.
- Release images are built on native AMD64 and ARM64 runners and are smoke-tested
  before publication. Do not add `config.yaml:image` until the public image is pullable.
- Guacamole JSON connections use the map key as the connection identifier; the
  JSON schema has no `name` field.
- Keep the image's musl-compatible base and dependencies in mind when changing
  the Python/Tomcat/Guacamole runtime.
- Ingress proxying must preserve relative URLs, WebSocket upgrades, and bodyless
  GET requests; test a real framebuffer when changing the tunnel.
- Bump the app version for releases and run the real-frame test against a fixture
  when the target connection path changes.
