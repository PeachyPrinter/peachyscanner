import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.image_2_points import Image2Points
from infrastructure.hardware import HardwareConfiguration
from infrastructure.roi import ROI


class PointConverterTest(unittest.TestCase):

    def setup_i2p(self, camera_pixels_shape_yx=(3, 3), camera_sensor_size_mm=(13.5, 13.5), intersections_rad_mm=[(np.pi / 4, 9)],):
        hardware = HardwareConfiguration(
            focal_length_mm=9,
            sensor_size_xy_mm=camera_sensor_size_mm,
            focal_point_to_center_mm=9,
            intersections_rad_mm=intersections_rad_mm,
            )
        return Image2Points(
            hardware,
            camera_pixels_shape_yx,
            )

    def assert_array(self, array1, array2, rtol=1e-05):
        self.assertTrue(array1.shape == array2.shape)
        for idx in range(array1.shape[0]):
            self.assertTrue(np.allclose(array1[idx], array2[idx], rtol=rtol), "TEST:{}:  {} == {}".format(idx, array1[idx], array2[idx]))

    def test_init_creates_expected_laser_plane_normals(self):
        a_rad = 0.785398163397
        b_rad = 0.844153986113
        c_rad = 0.909753157943

        expected_a_normal = np.array([9, 0, 9])
        expected_a_normal = expected_a_normal / np.linalg.norm(expected_a_normal)
        expected_b_normal = np.array([7.11111111118, 0, 8])
        expected_b_normal = expected_b_normal / np.linalg.norm(expected_b_normal)
        expected_c_normal = np.array([5.44444444452, 0, 7])
        expected_c_normal = expected_c_normal / np.linalg.norm(expected_c_normal)

        intersections_rad_mm = [(a_rad, 9), (b_rad, 8), (c_rad, 7)]
        i2p = self.setup_i2p(intersections_rad_mm=intersections_rad_mm)

        a_result = i2p.laser_plane_normals[a_rad]
        b_result = i2p.laser_plane_normals[b_rad]
        c_result = i2p.laser_plane_normals[c_rad]

        self.assert_array(expected_a_normal, a_result)
        self.assert_array(expected_b_normal, b_result)
        self.assert_array(expected_c_normal, c_result)


    def test_get_points_returns_expected_points_give_simple_camera_and_image(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx)
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([
            [-3.0, -3.0,  3.0],  # -1, -1
            [ 0,   -4.5,  0.0],  #  0, -1
            [ 9.0, -9.0, -9.0],  #  1, -1
            [-3.0,  0.0,  3.0],  # -1,  0 
            [ 0,    0.0,  0.0],  #  0,  0 
            [ 9.0,  0.0, -9.0],  #  1,  0 
            [-3.0,  3.0,  3.0],  # -1,  1 
            [ 0,    4.5,  0.0],  #  0,  1 
            [ 9.0,  9.0, -9.0],  #  1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result)


    def test_get_points_returns_expected_points_give_simple_camera_and_1_column(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx)
        image = np.zeros(camera_pixels_shape_yx).astype('bool')
        image[:, 0] = True

        expected = np.array([
            [-3.0, -3.0,  3.0],  # -1, -1
            [-3.0,  0.0,  3.0],  # -1,  0 
            [-3.0,  3.0,  3.0],  # -1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_should_rotate(self):
        camera_pixels_shape_yx = (3, 3)
        rotation = np.pi / 2.0
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx)
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([
            [ 3.0, -3.0,  3.0],  # -1, -1
            [ 0.0, -4.5,  0.0],  #  0, -1
            [-9.0, -9.0, -9.0],  #  1, -1
            [ 3.0,  0.0,  3.0],  # -1,  0 
            [ 0.0,  0.0,  0.0],  #  0,  0 
            [-9.0,  0.0, -9.0],  #  1,  0 
            [ 3.0,  3.0,  3.0],  # -1,  1 
            [ 0.0,  4.5,  0.0],  #  0,  1 
            [-9.0,  9.0, -9.0],  #  1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, rotation, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result, rtol=1e-03)

    def test_get_points_should_roi(self):
        camera_pixels_shape_yx = (4, 4)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx, camera_sensor_size_mm=(18, 18))
        image = np.ones((4, 4)).astype('bool')
        expected = np.array([
            [-3.0, -3.0,   3.0],  # -1, -1
            [ 0,   -4.5,  0.0],  #  0, -1
            [-3.0,  0.0,   3.0],  # -1,  0 
            [ 0,    0.0,  0.0],  #  0,  0 
            ], dtype='float16')

        roi = ROI(.25, .25, 0.5, 0.5)

        result = i2p.get_points(image, 0, roi, np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_should_return_nothing_when_ray_and_plane_dont_intersect(self):
        camera_pixels_shape_yx = (4, 4)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx, camera_sensor_size_mm=(20, 20))
        image = np.ones((4, 4)).astype('bool')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assertTrue(3, len(result))

    def test_get_points_should_work_on_real_sizes(self):
        camera_pixels_shape_yx = (480, 640)
        rotation = np.pi / 2.0
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx)
        image = np.zeros(camera_pixels_shape_yx).astype('uint8')
        image[:, 40] = 255

        result = i2p.get_points(image, rotation, ROI(0, 0, 1, 1), np.pi / 4)

        self.assertEquals(480, result.shape[0])

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
