from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("visualize", default_value="false"),
        DeclareLaunchArgument("robot_pose_topic", default_value="/robot/pose"),
        DeclareLaunchArgument("fsm_state_topic", default_value="/fsm/state"),
        DeclareLaunchArgument("trajectory_action_name", default_value="motion/execute_trajectory"),

        Node(
            package="manipulator_stack",
            executable="task_orchestrator_node",
            name="task_orchestrator_node",
            parameters=[
                {"visualize": LaunchConfiguration("visualize")},
                {"trajectory_action_name": LaunchConfiguration("trajectory_action_name")},
            ],
            remappings=[
                ("robot/pose", LaunchConfiguration("robot_pose_topic")),
                ("fsm/state", LaunchConfiguration("fsm_state_topic")),
                ("motion/execute_trajectory", LaunchConfiguration("trajectory_action_name")),
            ],
            respawn=True,
            respawn_delay=1,
        ),
    ])
