"""Verify a real framebuffer stream through the gateway's WebSocket tunnel."""

import asyncio

from aiohttp import ClientSession, WSMsgType


def instruction(opcode, *args):
    values = (opcode,) + args
    return ",".join(f"{len(value)}.{value}" for value in values) + ";"


def parse_instructions(data):
    """Parse complete Guacamole instructions, retaining a partial tail."""
    instructions = []
    position = 0
    while position < len(data):
        fields = []
        instruction_start = position
        while True:
            dot = data.find(".", position)
            if dot < 0:
                return instructions, data[instruction_start:]
            try:
                length = int(data[position:dot])
            except ValueError as error:
                raise ValueError("invalid Guacamole field length") from error
            value_start = dot + 1
            value_end = value_start + length
            if value_end >= len(data):
                return instructions, data[instruction_start:]
            fields.append(data[value_start:value_end])
            delimiter = data[value_end]
            position = value_end + 1
            if delimiter == ";":
                instructions.append(fields)
                break
            if delimiter != ",":
                raise ValueError("invalid Guacamole instruction delimiter")
    return instructions, ""


async def main() -> None:
    async with ClientSession() as session:
        async with session.post("http://127.0.0.1:8081/api/tokens", data="") as response:
            token = (await response.json())["authToken"]
        url = (
            "http://127.0.0.1:8081/websocket-tunnel?token=" + token
            + "&GUAC_DATA_SOURCE=json&GUAC_ID=rdp&GUAC_WIDTH=800"
            # GUAC_TYPE is the tunnel request type (c = connection), not the
            # backend protocol name. The selected connection is GUAC_ID=rdp.
            + "&GUAC_HEIGHT=600&GUAC_DPI=96&GUAC_TYPE=c"
            + "&GUAC_IMAGE=image/png&GUAC_IMAGE=image/jpeg"
        )
        async with session.ws_connect(url, protocols=("guacamole",), max_msg_size=0) as socket:
            print("PASS: WebSocket upgrade")
            message = await socket.receive(timeout=10)
            assert message.type == WSMsgType.TEXT, f"expected tunnel id, got {message.type}"
            # The first text message is the opaque tunnel identifier.
            # GUAC_TYPE=c selects an existing connection; the server performs
            # the connection handshake and then streams display instructions.
            buffer = ""
            image_streams = set()
            image_blobs = set()
            image_ends = set()
            seen = set()
            deadline = asyncio.get_running_loop().time() + 20
            while asyncio.get_running_loop().time() < deadline:
                try:
                    message = await socket.receive(timeout=5)
                except asyncio.TimeoutError:
                    break
                if message.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.ERROR):
                    break
                if message.type != WSMsgType.TEXT:
                    continue
                buffer += message.data
                instructions, buffer = parse_instructions(buffer)
                for fields in instructions:
                    opcode = fields[0]
                    seen.add(opcode)
                    if opcode == "error":
                        raise AssertionError("Guacamole tunnel returned an error")
                    if opcode == "sync" and len(fields) > 1:
                        await socket.send_str(instruction("sync", fields[1]))
                    if opcode == "rect":
                        seen.add("framebuffer")
                    elif opcode == "img" and len(fields) > 1:
                        image_streams.add(fields[1])
                    elif opcode == "blob" and len(fields) > 1:
                        image_blobs.add(fields[1])
                    elif opcode == "end" and len(fields) > 1:
                        image_ends.add(fields[1])
                if image_streams & image_blobs & image_ends or "framebuffer" in seen:
                    break
            assert image_streams & image_blobs & image_ends or "framebuffer" in seen, (
                f"no complete framebuffer stream: {sorted(seen)}"
            )
            print("PASS: RDP tunnel produced framebuffer instructions")


if __name__ == "__main__":
    asyncio.run(main())
