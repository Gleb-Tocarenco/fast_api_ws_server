import uuid
import random
import asyncio
from typing import Dict


class FlowGenerator:

    producer_channels: Dict[str, asyncio.Queue] = dict()

    def __init__(self):
        for i in range(1000):
            self.producer_channels[str(uuid.uuid4())] = asyncio.Queue()
        self.launch()

    async def _produce(self, queue: asyncio.Queue):
        while True:
            if queue.empty():
                await queue.put(random.random())
            await asyncio.sleep(5)

    def launch(self):
        asyncio.gather(*[self._produce(queue) for queue in self.producer_channels.values()])
