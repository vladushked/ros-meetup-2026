import asyncio

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AsyncNode(Node):
    def __init__(self):
        super().__init__("async_node_demo")
        self.pub = self.create_publisher(String, "demo/async_out", 10)

    async def business_loop(self):
        counter = 0
        while rclpy.ok():
            self.pub.publish(String(data=f"message #{counter}"))
            counter += 1
            await asyncio.sleep(0.2)

    async def ros_loop(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0)
            await asyncio.sleep(1e-4)


def main(args=None):
    rclpy.init(args=args)
    node = AsyncNode()

    try:
        done, _pending = asyncio.get_event_loop().run_until_complete(
            asyncio.wait(
                [node.ros_loop(), node.business_loop()],
                return_when=asyncio.FIRST_EXCEPTION,
            )
        )
        for task in done:
            task.result()
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
