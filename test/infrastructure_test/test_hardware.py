import unittest
import sys
import os
import logging
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.hardware import HardwareConfiguration


class HardwareConfigurationTest(unittest.TestCase):
    def test_hardware_config_should_raise_exception_if_sensor_size_is_not_a_tuple(self):
        with self.assertRaises(Exception):
            HardwareConfiguration(10, 10, 100, .68)

    def test_hardware_config_has_focal_length(self):
        focal_length = 10
        hardware_config = HardwareConfiguration(focal_length, (10, 7.5), 100, 0.68)
        self.assertEquals(focal_length, hardware_config.focal_length_mm)

    def test_hardware_config_has_sensor_size(self):
        sensor_size = (10, 7.5)
        hardware_config = HardwareConfiguration(10, (10, 7.5), 100, 0.68)
        self.assertEquals(sensor_size, hardware_config.sensor_size_xy_mm)

    def test_hardware_config_has_focal_points_to_center(self):
        focal_point_to_center_mm = 100
        hardware_config = HardwareConfiguration(10, (10, 7.5), focal_point_to_center_mm, 0.68)
        self.assertEquals(focal_point_to_center_mm, hardware_config.focal_point_to_center_mm)

    def test_hardware_config_has_laser_center_intersection_rad(self):
        laser_center_intersection_rad = 0.66
        hardware_config = HardwareConfiguration(10, (10, 7.5), 100, laser_center_intersection_rad)
        self.assertEquals(laser_center_intersection_rad, hardware_config.laser_center_intersection_rad)

    def test_hardware_config_has_center_intersection_xyz(self):
        focal_point_to_center_mm = 100
        expected = np.array([0, 0, -100])
        hardware_config = HardwareConfiguration(10, (10, 7.5), focal_point_to_center_mm, 0.68)
        self.assertTrue((expected == hardware_config.center_intersection_xyz).all())

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
