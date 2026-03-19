import asyncio
from pathlib import Path

from std_msgs.msg import String

from node_base import AsyncBaseNode, base_main, register_loop


class SimpleAsyncPubNode(AsyncBaseNode):
    def __init__(self):
        super().__init__(
            package_name="demo_pkg",
            node_name="simple_async_pub_node",
            params_file=Path("simple_async_pub_node.yaml"),
        )

    def init_params(self) -> None:
        self.declare_parameter("period_sec", 0.5)
        self.period_sec = float(self.get_parameter("period_sec").value)

    def init_ros_interfaces(self) -> None:
        self.pub = self.create_publisher(String, "async/out", 10)

    @register_loop
    async def heartbeat_loop(self):
        while True:
            self.pub.publish(String(data=f"tick"))
            await asyncio.sleep(self.period_sec)

def main(args=None):
    return base_main(SimpleAsyncPubNode, args=args)
