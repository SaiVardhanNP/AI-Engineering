import asyncio
import json
import websockets


async def main():

    async with websockets.connect("ws://127.0.0.1:8000/ws") as websocket:
        request = {
            "call_id": "call_001",
            "tool_name": "search_files",
            "arguments": {"query":"calculator"},
        }

        print("Sending request:")
        print(json.dumps(request, indent=2))

        await websocket.send(json.dumps(request))

        response = await websocket.recv()

        print("\nReceived result:")
        print(response)


asyncio.run(main())
