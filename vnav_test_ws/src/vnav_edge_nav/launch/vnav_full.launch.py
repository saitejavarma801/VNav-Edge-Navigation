from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # -------- Navigation Node --------
    hybrid_node = Node(
        package='vnav_edge_nav',
        executable='hybrid_nav',
        name='hybrid_visual_navigator',
        output='screen'
    )

    # -------- Trajectory Monitor --------
    trajectory_node = Node(
        package='vnav_edge_nav',
        executable='trajectory_monitor',
        name='trajectory_monitor',
        output='screen'
    )

    # -------- Metrics Logger --------
    metrics_node = Node(
        package='vnav_edge_nav',
        executable='vnav_metrics_logger',
        name='vnav_metrics_logger',
        output='screen'
    )

    # -------- Launch All --------
    return LaunchDescription([
        hybrid_node,
        trajectory_node,
        metrics_node
    ])
