"""LOCAL-ONLY WebSocket audio loopback, Article 08.

Run: python -m pip install 'websockets>=16,<17'; python server.py
Open index.html through python -m http.server 8008 bound to 127.0.0.1.
This lab transports raw float32 mono samples unchanged (not a voice agent).
"""
import asyncio
import json
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

ALLOWED_ORIGINS = ["http://127.0.0.1:8008", "http://localhost:8008"]

async def echo_audio(socket):
    ready = False
    try:
        async for message in socket:
            if isinstance(message, str):
                if len(message) > 512:
                    await socket.close(code=1009, reason="control message too big")
                    return
                try:
                    command = json.loads(message)
                except json.JSONDecodeError:
                    await socket.close(code=1003, reason="invalid JSON")
                    return
                rate = command.get("sample_rate") if isinstance(command, dict) else None
                if (not isinstance(rate, (int, float)) or isinstance(rate, bool)
                        or not (8000 <= rate <= 192000)):
                    await socket.close(code=1003, reason="invalid sample rate")
                    return
                ready = True
                await socket.send(json.dumps({"type": "ready", "sample_rate": rate}))
                continue
            if not ready:
                await socket.close(code=1008, reason="send sample rate first")
                return
            if len(message) == 0 or len(message) > 65536 or len(message) % 4 != 0:
                await socket.close(code=1009, reason="invalid float32 frame")
                return
            await socket.send(message)
    except ConnectionClosed:
        pass


async def main():
    # Bound to localhost, with an explicit browser Origin allowlist.
    async with serve(echo_audio, "127.0.0.1", 8765,
                     origins=ALLOWED_ORIGINS,
                     max_size=65536,
                     compression=None,
                     max_queue=8,
                     write_limit=32768) as server:
        print("WebSocket loopback ready: ws://127.0.0.1:8765 (local only)")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
