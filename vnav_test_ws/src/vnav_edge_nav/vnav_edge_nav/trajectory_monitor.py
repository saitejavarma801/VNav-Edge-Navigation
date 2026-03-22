#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path


class TrajectoryMonitor(Node):

    def __init__(self):
        super().__init__('trajectory_monitor')

        self.create_subscription(
            Path,
            '/vnav_path',
            self.path_callback,
            10)

        self.get_logger().info("Trajectory Monitor Started")

    def path_callback(self, msg):
        pass  # RViz handles visualization


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
