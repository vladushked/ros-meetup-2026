import asyncio

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from task_fsm import TaskFSM


class FsmDriverNode(Node):
    def __init__(self):
        super().__init__("fsm_driver_node")
        self.state_pub = self.create_publisher(String, "fsm/state", 10)
        self.fsm = TaskFSM(self.get_logger())

    async def ros_loop(self):
        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0)
            await asyncio.sleep(1e-4)

    async def fsm_loop(self):
        while rclpy.ok():
            await self.fsm.step()
            if self.fsm.updated:
                self.state_pub.publish(String(data=self.fsm.state))
                self.fsm.updated = False
            await asyncio.sleep(1e-3)

    async def scenario_loop(self):
        await asyncio.sleep(0.2)
        self.fsm.set_transition(TaskFSM.Transition.OK)
        await asyncio.sleep(0.5)
        self.fsm.set_transition(TaskFSM.Transition.START)
        await asyncio.sleep(1.0)
        self.fsm.set_transition(TaskFSM.Transition.HALT)


def main(args=None):
    rclpy.init(args=args)
    node = FsmDriverNode()
    try:
        done, _pending = asyncio.get_event_loop().run_until_complete(
            asyncio.wait(
                [node.ros_loop(), node.fsm_loop(), node.scenario_loop()],
                return_when=asyncio.FIRST_EXCEPTION,
            )
        )
        for task in done:
            task.result()
    finally:
        node.destroy_node()


if __name__ == "__main__":
    main()
