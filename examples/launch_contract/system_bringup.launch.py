from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("visualize", default_value="false"),
        DeclareLaunchArgument("robot_pose_topic", default_value="/robot/pose"),
        DeclareLaunchArgument("fsm_state_topic", default_value="/fsm/state"),
        DeclareLaunchArgument("trajectory_action_name", default_value="motion/execute_trajectory"),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                str(Path(get_package_share_directory("manipulator_stack"), "launch", "manipulator_stack.launch.py"))
            ),
            launch_arguments={
                "visualize": LaunchConfiguration("visualize"),
                "robot_pose_topic": LaunchConfiguration("robot_pose_topic"),
                "fsm_state_topic": LaunchConfiguration("fsm_state_topic"),
                "trajectory_action_name": LaunchConfiguration("trajectory_action_name"),
            }.items(),
        ),

        Node(
            package="rqt_gui",
            executable="rqt_gui",
            condition=IfCondition(LaunchConfiguration("visualize")),
        ),
    ])
