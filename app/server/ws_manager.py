import asyncio
from functools import cached_property
from typing import List, Dict, Optional
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosedError

from app.flow_generator.flow_generator import FlowGenerator


channels_lock = asyncio.Lock()


class WSManager:

    def __init__(self):
        self.channels: Dict[str: Dict[int, WebSocket]] = dict()
        self.generator = FlowGenerator()
        asyncio.create_task(self.broadcast())

    @cached_property
    def available_channels(self):
        return list(self.generator.producer_channels.keys())

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        async with channels_lock:
            if channel in self.channels:
                self.channels[channel].update({id(websocket): websocket})
            else:
                self.channels[channel] = {id(websocket): websocket}

    async def update(self, websocket: WebSocket, channel_list: List[str], ) -> None:
        channels_to_update = self.channels.keys() - set(channel_list)
        for channel in channels_to_update:
            async with channels_lock:
                self.channels[channel].pop(id(websocket), None)
        for channel in channel_list:
            await self.connect(websocket, channel)

    async def disconnect(self, websocket: WebSocket, channel: Optional[str] = None) -> None:
        if channel in self.channels:
            async with channels_lock:
                self.channels[channel].pop(id(websocket), None)
        else:
            for channel in self.channels:
                self.channels[channel].pop(id(websocket), None)

    async def send(self, websocket: WebSocket, data: Dict[str, str]) -> None:
        try:
            await websocket.send_json(data)
        except ConnectionClosedError:
            pass

    async def broadcast(self) -> None:
        while True:
            await asyncio.sleep(0.01)
            async with channels_lock:
                for channel, websockets in self.channels.items():
                    item = await self.generator.producer_channels[channel].get()
                    for websocket in websockets.values():
                        await self.send(websocket, {'data': item, 'channel': channel})
