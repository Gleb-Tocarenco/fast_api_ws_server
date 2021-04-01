from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.utils import validate_message
from .ws_manager import WSManager


app = FastAPI()
connection_manager = WSManager()


@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.get('/channels/')
async def get_routes():
    return {"channels": connection_manager.available_channels}


@app.websocket('/ws/')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            print(message)
            try:
                validate_message(message)
            except AssertionError:
                await connection_manager.send(websocket, {"error": "invalid message"})
                continue
            channel = message['channel']
            action = message['action']

            if type(channel) == str and channel not in connection_manager.available_channels:
                await connection_manager.send(websocket, {"error": "wrong channel"})
                continue
            if type(channel) == list and not all(c in connection_manager.available_channels for c in channel):
                await connection_manager.send(websocket, {"error": "wrong channel"})
                continue
            if action == "update" and type(channel) == str:
                await connection_manager.send(websocket, {"error": "wrong format"})
                continue

            if action == "connect":
                await connection_manager.connect(websocket, channel)
            elif action == "disconnect":
                await connection_manager.disconnect(websocket, channel)
            elif action == "update":
                await connection_manager.update(websocket, channel)
            else:
                await connection_manager.send(websocket, {"error": "invalid action"})
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
