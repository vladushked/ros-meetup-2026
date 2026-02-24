import asyncio

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def register_loop(loop):
    loop.registered = True
    return loop


class AsyncOrchestrator(Node):
    async_loops = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.async_loops = []
        for clsattr in cls.__dict__.values():
            if callable(clsattr) and getattr(clsattr, "registered", False):
                cls.async_loops.append(clsattr)

    def __init__(self):
        super().__init__("task_orchestrator_node")
        self.state_pub = self.create_publisher(String, "fsm/state", 10)
        self.status_pub = self.create_publisher(String, "system/status", 10)
        self._state = "READY"

    @register_loop
    async def ros_loop(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0)
            await asyncio.sleep(1e-4)

    @register_loop
    async def grasping_loop(self):
        while rclpy.ok():
            self.status_pub.publish(String(data="grasping loop alive"))
            await asyncio.sleep(0.2)

    @register_loop
    async def fsm_loop(self):
        while rclpy.ok():
            self.state_pub.publish(String(data=self._state))
            await asyncio.sleep(0.5)

    @register_loop
    async def watchdog_loop(self):
        while rclpy.ok():
            self.get_logger().info("watchdog loop check")
            await asyncio.sleep(1.0)

    def run(self):
        done, _pending = asyncio.get_event_loop().run_until_complete(
            asyncio.wait([loop(self) for loop in self.async_loops], return_when=asyncio.FIRST_EXCEPTION)
        )
        for task in done:
            task.result()


def main(args=None):
    rclpy.init(args=args)
    node = AsyncOrchestrator()
    try:
        node.run()
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
