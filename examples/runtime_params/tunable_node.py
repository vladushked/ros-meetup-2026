from pathlib import Path

from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter
from std_msgs.msg import Float32

from node_base import BaseNode, base_main


class TunableNode(BaseNode):
    def __init__(self):
        super().__init__(
            package_name="demo_pkg",
            node_name="tunable_node",
            params_file=Path("tunable_node.yaml"),
        )

    def init_params(self) -> None:
        self.declare_parameter("gain", 1.0)
        self.declare_parameter("bias", 0.0)
        self.gain = float(self.get_parameter("gain").value)
        self.bias = float(self.get_parameter("bias").value)

    def init_ros_interfaces(self) -> None:
        self.pub = self.create_publisher(Float32, "control/output", 10)
        self.timer = self.create_timer(0.2, self.on_timer)

    def on_timer(self) -> None:
        value = self.gain * 10.0 + self.bias
        self.pub.publish(Float32(data=float(value)))

    def update_params(self, param_list: list[Parameter]) -> SetParametersResult:
        for param in param_list:
            if param.name == "gain":
                self.gain = float(param.value)
            elif param.name == "bias":
                self.bias = float(param.value)
        return super().update_params(param_list)


def main(args=None):
    return base_main(TunableNode, args=args)
