# VNav-Edge-Navigation
A ROS 2 Python package for edge-based visual navigation in structured indoor environments. The package provides a lightweight navigation stack that uses RGB, depth, and IMU data to generate motion commands, publish an estimated path, broadcast robot pose through TF, and log runtime metrics for analysis.

## Overview

This repository contains a modular visual navigation system built around three core components:

- **Hybrid Visual Navigation Node** for perception-driven motion control
- **Trajectory Monitor** for path observation and visualization support
- **Metrics Logger** for CSV-based runtime data collection
----
## Hardware Requirement

This project uses the following primary sensor:

- **Intel RealSense Depth Camera D455**
-----


**1.Hybrid Visual Navigation Node**

The main navigation node processes RGB, depth, and IMU streams to perform reactive navigation. It estimates lateral corridor balance from depth data, detects frontal obstacles, and publishes velocity commands accordingly.


Subscribe to RGB image, depth image, and IMU data
Compute steering corrections from perceived corridor geometry
Detect nearby frontal obstacles
Publish velocity commands
Publish estimated path information
Broadcast map -> base_link TF

**2.Trajectory Monitor**

The trajectory monitor subscribes to the generated path topic and provides a simple monitoring interface for validating the navigation output during runtime.
Subscribe to the path topic
Support live trajectory observation in tools such as RViz

**3.Metrics Logger**

The metrics logger records robot state and control commands to CSV files for offline analysis and performance evaluation.

**Logged metrics**

Timestamp

Position: x, y

Orientation: theta

Linear velocity command

Angular velocity command

**Subscribed Topics**

/camera/camera/color/image_raw

/camera/camera/depth/image_rect_raw

/camera/camera/gyro/sample

/vnav_path

**Published Topics**

/cmd_vel

/vnav_path

**TF Frames**

map -> base_link

/tf

/cmd_vel

**Build**

    colcon build --packages-select vnav_edge_nav
    source install/setup.bash

**Launch**

    ros2 launch vnav_edge_nav vnav_full.launch.py


**RealSense_depth_cam**

Download the Intel Realsense depth camera repository from github and then launch

    ros2 launch realsense2_camera rs_launch.py



## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software with proper attribution.

See the `LICENSE` file for full details.
