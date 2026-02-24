from pathlib import Path

from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter
from std_msgs.msg import String

from node_base import BaseNode, base_main


class SimpleSyncNode(BaseNode):
    def __init__(self):
        super().__init__(
            package_name="demo_pkg",
            node_name="simple_sync_node",
            params_file=Path("simple_sync_node.yaml"),
        )

    def init_params(self) -> None:
        self.declare_parameter("message", "hello")

    def init_ros_interfaces(self) -> None:
        self.pub = self.create_publisher(String, "sync/out", 10)
        self.timer = self.create_timer(1.0, self.on_timer)

    def on_timer(self) -> None:
        self.pub.publish(String(data=self.get_parameter("message").value))

    def update_params(self, param_list: list[Parameter]) -> SetParametersResult:
        result = super().update_params(param_list)
        return result


def main(args=None):
    return base_main(SimpleSyncNode, args=args)
