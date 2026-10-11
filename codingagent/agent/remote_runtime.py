from local_runtime.protocol import ToolRequest, ToolResult
import json
import websockets


class RemoteRuntimeClient:
    def __init__(self, url: str):
        self.url = url

    async def execute(self, request: ToolRequest) -> ToolRequest:
        async with websockets.connect(self.url) as websocket:
            await websocket.send(json.dumps(request.model_dump()))

            response = await websocket.recv()

            return ToolResult.model_validate(json.loads(response))
