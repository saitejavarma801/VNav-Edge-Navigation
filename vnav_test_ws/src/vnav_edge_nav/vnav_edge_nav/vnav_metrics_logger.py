#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Path
from tf2_msgs.msg import TFMessage
import os
import csv
from datetime import datetime
import math


class VNavMetricsLogger(Node):

    def __init__(self):
        super().__init__('vnav_metrics_logger')

        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.linear_x = 0.0
        self.angular_z = 0.0

        # -------- Subscribers --------
        self.create_subscription(Twist, '/cmd_vel', self.cmd_callback, 10)
        self.create_subscription(Path, '/vnav_path', self.path_callback, 10)
        self.create_subscription(TFMessage, '/tf', self.tf_callback, 10)

        # -------- Logging Setup --------
        self.setup_logging()

        # Timer to log periodically
        self.timer = self.create_timer(0.1, self.log_metrics)

        self.get_logger().info("VNav Metrics Logger Started")

    # =============================
    # LOGGING SETUP
    # =============================

    def setup_logging(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base_dir, "logs")

        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            self.get_logger().info("Logs folder created")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = os.path.join(logs_dir, f"metrics_{timestamp}.csv")

        self.log_file = open(self.log_file_path, mode='w', newline='')
        self.csv_writer = csv.writer(self.log_file)

        self.csv_writer.writerow([
            "timestamp",
            "x", "y", "theta",
            "linear_x", "angular_z"
        ])

        self.get_logger().info(f"Logging to {self.log_file_path}")

    # =============================
    # CALLBACKS
    # =============================

    def cmd_callback(self, msg):
        self.linear_x = msg.linear.x
        self.angular_z = msg.angular.z

    def path_callback(self, msg):
        if len(msg.poses) > 0:
            last_pose = msg.poses[-1]
            self.x = last_pose.pose.position.x
            self.y = last_pose.pose.position.y

            qz = last_pose.pose.orientation.z
            qw = last_pose.pose.orientation.w
            self.theta = 2 * math.atan2(qz, qw)

    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id == "base_link":
                self.x = transform.transform.translation.x
                self.y = transform.transform.translation.y

                qz = transform.transform.rotation.z
                qw = transform.transform.rotation.w
                self.theta = 2 * math.atan2(qz, qw)

    # =============================
    # LOG LOOP
    # =============================

    def log_metrics(self):

        now = self.get_clock().now().nanoseconds

        self.csv_writer.writerow([
            now,
            self.x,
            self.y,
            self.theta,
            self.linear_x,
            self.angular_z
        ])

        self.log_file.flush()


def main(args=None):
    rclpy.init(args=args)
    node = VNavMetricsLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
