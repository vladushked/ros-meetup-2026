import asyncio
from typing import AsyncIterator

from rclpy.node import Node


class AsyncSubscription:
    def __init__(self, node: Node, msg_type, topic: str, qos=10):
        self.queue = asyncio.Queue(maxsize=qos)
        node.create_subscription(msg_type, topic, self._cb, qos)

    def _cb(self, msg):
        if self.queue.full():
            _ = self.queue.get_nowait()
        self.queue.put_nowait(msg)

    async def messages(self) -> AsyncIterator:
        while True:
            yield await self.queue.get()
