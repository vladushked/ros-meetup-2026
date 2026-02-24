import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

import rclpy
import yaml
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from rclpy.parameter import Parameter


def register_loop(loop: Callable):
    loop.registered = True
    return loop


class BaseNodeAbstract(ABC, Node):
    @abstractmethod
    def init_params(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def init_ros_interfaces(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_params(self, param_list: list[Parameter]) -> SetParametersResult:
        raise NotImplementedError


class BaseNode(BaseNodeAbstract):
    dynamic_params: bool = True

    def __init__(self, package_name: str, node_name: str, params_file: Path):
        super().__init__(node_name)
        self.package_name = package_name
        self.params_file = params_file

        self.declare_parameter("visualize", False)
        self.visualize = self.get_parameter("visualize").value

        self.init_params()
        if self.dynamic_params:
            self.add_on_set_parameters_callback(self.update_params)
        self.init_ros_interfaces()

    def save_params(self, param_list: list[Parameter]) -> None:
        params = {
            self.get_name(): {
                "ros__parameters": {p.name: p.value for p in self._parameters.values()}
            }
        }
        for p in param_list:
            params[self.get_name()]["ros__parameters"][p.name] = p.value

        with self.params_file.open("w", encoding="utf-8") as f:
            yaml.safe_dump(params, f, default_flow_style=False, allow_unicode=True)

    def update_params(self, param_list: list[Parameter]) -> SetParametersResult:
        if self.dynamic_params:
            self.save_params(param_list)
        return SetParametersResult(successful=True)

    def init_params(self) -> None:
        pass

    def init_ros_interfaces(self) -> None:
        pass


class AsyncBaseNode(BaseNode):
    async_loops: list[Callable] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.async_loops = []
        for basecls in cls.__bases__:
            for clsattr in basecls.__dict__.values():
                if callable(clsattr) and getattr(clsattr, "registered", False):
                    cls.async_loops.append(clsattr)
        for clsattr in cls.__dict__.values():
            if callable(clsattr) and getattr(clsattr, "registered", False):
                cls.async_loops.append(clsattr)

    @register_loop
    async def ros_loop(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0)
            await asyncio.sleep(1e-4)

    def run(self) -> None:
        event_loop = asyncio.get_event_loop()
        futures = [loop(self) for loop in self.async_loops]
        done, _pending = event_loop.run_until_complete(
            asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
        )
        for task in done:
            task.result()


def base_main(node_cls: type[BaseNode], args=None) -> int:
    rclpy.init(args=args)
    node = node_cls()
    try:
        if issubclass(node_cls, AsyncBaseNode):
            node.run()
        else:
            rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
    return 0
