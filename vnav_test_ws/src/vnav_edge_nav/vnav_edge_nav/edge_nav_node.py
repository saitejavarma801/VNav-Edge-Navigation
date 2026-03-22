#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import Image, Imu
from geometry_msgs.msg import Twist
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped, TransformStamped

from tf2_ros import TransformBroadcaster
from cv_bridge import CvBridge

import cv2
import numpy as np
import math


class HybridVisualNavigator(Node):

    def __init__(self):
        super().__init__('hybrid_visual_navigator')

        self.bridge = CvBridge()

        self.rgb_frame = None
        self.depth_frame = None

        self.prev_error = 0.0

        # ================= TF STATE =================
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.forward_speed = 0.15  # SAME as controller speed
        self.dt = 0.1

        self.tf_broadcaster = TransformBroadcaster(self)

        # ================= PATH =================
        self.path_pub = self.create_publisher(Path, '/vnav_path', 10)
        self.path_msg = Path()
        self.path_msg.header.frame_id = "map"

        # -------- Subscribers --------
        self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.rgb_callback,
            10)

        self.create_subscription(
            Image,
            '/camera/camera/depth/image_rect_raw',
            self.depth_callback,
            10)

        imu_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        self.create_subscription(
            Imu,
            '/camera/camera/gyro/sample',
            self.imu_callback,
            imu_qos)

        # -------- Publisher --------
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer loop
        self.timer = self.create_timer(self.dt, self.process_loop)

        cv2.namedWindow("HYBRID_NAV", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("HYBRID_NAV", 1400, 700)

        self.get_logger().info("Hybrid Corridor Navigator + TF Started")

    # =============================
    # Callbacks
    # =============================

    def rgb_callback(self, msg):
        self.rgb_frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

    def depth_callback(self, msg):
        self.depth_frame = (
            self.bridge.imgmsg_to_cv2(msg, 'passthrough')
            .astype(np.float32) / 1000.0
        )

    def imu_callback(self, msg):
        # integrate yaw
        self.yaw += msg.angular_velocity.z * self.dt

    # =============================
    # TF PUBLISHER
    # =============================

    def publish_tf(self):

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "map"
        t.child_frame_id = "base_link"

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0

        # Convert yaw to quaternion
        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

    # =============================
    # Main Processing Loop
    # =============================

    def process_loop(self):

        if self.rgb_frame is None or self.depth_frame is None:
            return

        frame = self.rgb_frame.copy()
        depth = self.depth_frame.copy()

        h_depth, w_depth = depth.shape
        midpoint = w_depth // 2

        scan_row = int(h_depth * 0.45)
        band = depth[scan_row-5:scan_row+5, :]
        band[(band == 0) | (band > 6.0)] = np.nan

        if band.size == 0 or np.isnan(band).all():
            return

        scan = np.nanmedian(band, axis=0)

        left_vals = scan[:midpoint]
        right_vals = scan[midpoint:]

        left_vals = left_vals[left_vals > 0]
        right_vals = right_vals[right_vals > 0]

        if len(left_vals) < 10 or len(right_vals) < 10:
            return

        left_dist = np.median(left_vals)
        right_dist = np.median(right_vals)

        lateral_error = right_dist - left_dist

        # Front detection
        front_band = depth[int(h_depth * 0.4):int(h_depth * 0.6),
                           midpoint - 20: midpoint + 20]

        front_band[(front_band == 0) | (front_band > 6.0)] = np.nan

        if front_band.size > 0 and not np.isnan(front_band).all():
            front_dist = np.nanmedian(front_band)
        else:
            front_dist = 5.0

        twist = Twist()

        if front_dist < 0.6:
            twist.linear.x = 0.0
            twist.angular.z = 0.5
        else:
            twist.linear.x = self.forward_speed
            angular_gain = 0.4
            angular_cmd = -lateral_error * angular_gain
            angular_cmd = 0.7 * self.prev_error + 0.3 * angular_cmd
            self.prev_error = angular_cmd
            twist.angular.z = angular_cmd

        self.cmd_pub.publish(twist)

        # ================= UPDATE POSITION =================
        self.x += twist.linear.x * math.cos(self.yaw) * self.dt
        self.y += twist.linear.x * math.sin(self.yaw) * self.dt

        # Publish TF
        self.publish_tf()

        # Publish Path
        pose = PoseStamped()
        pose.header.frame_id = "map"
        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        self.path_msg.poses.append(pose)
        self.path_pub.publish(self.path_msg)

        # Debug
        cv2.putText(frame,
                    f"L:{left_dist:.2f} R:{right_dist:.2f}",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2)

        cv2.imshow("HYBRID_NAV", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = HybridVisualNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

