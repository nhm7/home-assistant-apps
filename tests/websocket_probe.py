"""Verify the gateway accepts a Guacamole WebSocket upgrade.

Run inside the gateway container after startup. Payloads and tokens are never
printed; without an RDP server, a tunnel error/close is an expected result.
"""

import asyncio

from aiohttp import ClientSession, WSMsgType


async def main() -> None:
    async with ClientSession() as session:
        async with session.post("http://127.0.0.1:8081/api/tokens", data="") as response:
            token = (await response.json())["authToken"]
        url = (
            "http://127.0.0.1:8081/websocket-tunnel?token=" + token
            + "&GUAC_DATA_SOURCE=json&GUAC_ID=rdp&GUAC_WIDTH=800"
            + "&GUAC_HEIGHT=600&GUAC_DPI=96"
        )
        async with session.ws_connect(url, protocols=("guacamole",), max_msg_size=0) as socket:
            print("PASS: WebSocket upgrade")
            message = await socket.receive(timeout=10)
            assert message.type in (WSMsgType.TEXT, WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR)
            print("PASS: tunnel response received")


if __name__ == "__main__":
    asyncio.run(main())
