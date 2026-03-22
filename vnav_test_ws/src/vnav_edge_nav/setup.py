from setuptools import setup
import os
from glob import glob

package_name = 'vnav_edge_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='orin',
    maintainer_email='orin@todo.todo',
    description='Visual navigation with trajectory monitor',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hybrid_nav = vnav_edge_nav.edge_nav_node:main',
            'trajectory_monitor = vnav_edge_nav.trajectory_monitor:main',
	    'vnav_metrics_logger = vnav_edge_nav.vnav_metrics_logger:main',
        ],
    },
)
