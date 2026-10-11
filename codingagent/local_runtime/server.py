from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from local_runtime.protocol import ToolRequest, ToolResult
from local_runtime.runtime import LocalRuntime

app = FastAPI()

runtime = LocalRuntime("workspace/sample-project")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("Backend connected")
    try:
        while True:
            message = await websocket.receive_json()
            print("Received: ", message)

            request = ToolRequest.model_validate(message)

            result = runtime.execute(request=request)

            await websocket.send_json(result.model_dump())
    except WebSocketDisconnect:
        print("Backend Disconnected")
