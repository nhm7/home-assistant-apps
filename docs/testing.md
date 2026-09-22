# RDP Gateway testing

Run the option-mapping and translation-coverage tests from the repository
root:

```sh
python3 tests/test_rdp_options.py
```

For a running image, mount a test options file and run the HTTP smoke test:

```sh
docker run --rm --detach --name rdp-gateway \
  --publish 18081:8081 \
  --volume "$PWD/tests/options.json:/data/options.json:ro" \
  ghcr.io/nhm7/amd64-rdp-gateway:0.1.12
python3 tests/smoke.py http://127.0.0.1:18081
docker rm --force rdp-gateway
```

The smoke test checks Guacamole readiness, automatic authentication, and that
the configured RDP connection is exposed. `tests/websocket_probe.py` can be
used with a reachable RDP fixture to verify that a framebuffer is streamed.

For an isolated disposable xrdp target, build and run the fixture on a private
Docker network:

```sh
sudo docker build -t local/xrdp-fixture:24.04 tests/xrdp-fixture
sudo docker network create rdp-fixture-net
sudo docker run -d --name xrdp-fixture --network rdp-fixture-net local/xrdp-fixture:24.04
sudo docker run --rm --name rdp-gateway-fixture --network rdp-fixture-net \
  --publish 127.0.0.1:18084:8081 \
  --volume "$PWD/tests/options-xrdp-fixture.json:/data/options.json:ro" \
  local/rdp-gateway:0.1.12
```

In another terminal, run the smoke test and WebSocket probe:

```sh
python3 tests/smoke.py http://127.0.0.1:18084
sudo docker cp tests/websocket_probe.py rdp-gateway-fixture:/tmp/
sudo docker exec rdp-gateway-fixture python3 /tmp/websocket_probe.py
```

The fixture uses synthetic credentials and a self-signed certificate only.
After testing, stop the containers and remove `rdp-fixture-net`.
