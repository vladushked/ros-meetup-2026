import asyncio
from pathlib import Path

from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter
from std_msgs.msg import String

from node_base import AsyncBaseNode, base_main, register_loop


class SimpleAsyncNode(AsyncBaseNode):
    def __init__(self):
        super().__init__(
            package_name="demo_pkg",
            node_name="simple_async_node",
            params_file=Path("simple_async_node.yaml"),
        )

    def init_params(self) -> None:
        self.declare_parameter("period_sec", 0.5)
        self.period_sec = float(self.get_parameter("period_sec").value)

    def init_ros_interfaces(self) -> None:
        self.pub = self.create_publisher(String, "async/out", 10)

    def update_params(self, param_list: list[Parameter]) -> SetParametersResult:
        for param in param_list:
            if param.name == "period_sec":
                self.period_sec = float(param.value)
        return super().update_params(param_list)

    @register_loop
    async def heartbeat_loop(self):
        counter = 0
        while True:
            self.pub.publish(String(data=f"tick: {counter}"))
            counter += 1
            await asyncio.sleep(self.period_sec)


def main(args=None):
    return base_main(SimpleAsyncNode, args=args)
