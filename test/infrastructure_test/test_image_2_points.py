import unittest
import sys
import os
import numpy as np
from math import atan, sqrt, cos, sin
import logging

from mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.image_2_points import Image2Points
from infrastructure.hardware import HardwareConfiguration
from infrastructure.roi import ROI


class PointConverterTest(unittest.TestCase):

    def setup_i2p(
            self,
            focal_length_mm=9,
            camera_pixels_shape_yx=(3, 3),
            camera_sensor_size_mm_xy=(13.5, 13.5),
            intersections_rad_mm=[(np.pi / 4, 9)],
            focal_point_to_center_mm=9):
        hardware = HardwareConfiguration(
            focal_length_mm=focal_length_mm,
            sensor_size_xy_mm=camera_sensor_size_mm_xy,
            focal_point_to_center_mm=focal_point_to_center_mm,
            intersections_rad_mm=intersections_rad_mm)
        return Image2Points(hardware, camera_pixels_shape_yx)

    def assert_array(self, array1, array2, atol=1e-02):
        self.assertTrue(array1.shape == array2.shape)
        for idx in range(array1.shape[0]):
            self.assertTrue(np.allclose(array1[idx], array2[idx], atol=atol), "TEST:{}:  {} == {}".format(idx, array1[idx], array2[idx]))

    def test_init_creates_expected_laser_plane_normals_1(self):
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

    def test_init_creates_expected_laser_plane_normals_2(self):
        a_rad = np.pi / 4

        expected_a_normal = np.array([9, 0, 9])
        expected_a_normal = expected_a_normal / np.linalg.norm(expected_a_normal)

        i2p = self.setup_i2p(
            camera_pixels_shape_yx=(3, 3),
            camera_sensor_size_mm_xy=(3.0, 3.0),
            focal_length_mm=3.0,
            intersections_rad_mm=[(np.pi / 4, 9)])

        a_result = i2p.laser_plane_normals[a_rad]
        self.assert_array(expected_a_normal, a_result)

    def test_get_points_returns_expected_points_give_simple_camera_and_image_at_0cm(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            camera_sensor_size_mm_xy=(3.0, 3.0),
            focal_length_mm=3.0,
            intersections_rad_mm=[(np.pi / 4, 9)]
        )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -2.250,    2.250,    2.250, ],
                             [  -0.000,    3.000,    0.000, ],
                             [   4.500,    4.500,   -4.500, ],
                             [  -2.250,    0.000,    2.250, ],
                             [  -0.000,    0.000,    0.000, ],
                             [   4.500,    0.000,   -4.500, ],
                             [  -2.250,   -2.250,    2.250, ],
                             [  -0.000,   -3.000,    0.000, ],
                             [   4.500,   -4.500,   -4.500, ],
                             ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_simple_camera_and_image_at_1cm(self):
        camera_pixels_shape_yx = (3, 3)
        b_rad = 0.844153986113

        intersections_rad_mm = [(b_rad, 8)]
        i2p = self.setup_i2p(
            camera_sensor_size_mm_xy=(3, 3),
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            intersections_rad_mm=intersections_rad_mm,
            focal_length_mm=3.0,
            )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -2.057,    2.057,    2.829, ],
                             [  -0.000,    2.667,    1.000, ],
                             [   3.789,    3.789,   -2.368, ],
                             [  -2.057,    0.000,    2.829, ],
                             [  -0.000,    0.000,    1.000, ],
                             [   3.789,    0.000,   -2.368, ],
                             [  -2.057,   -2.057,    2.829, ],
                             [  -0.000,   -2.667,    1.000, ],
                             [   3.789,   -3.789,   -2.368, ]], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), b_rad)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_simple_camera_and_image_at_2_cm(self):
        camera_pixels_shape_yx = (3, 3)
        c_rad = 0.909753157943

        intersections_rad_mm = [(c_rad, 7)]
        i2p = self.setup_i2p(
            camera_sensor_size_mm_xy=(3, 3),
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            intersections_rad_mm=intersections_rad_mm,
            focal_length_mm=3.0,
            )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -1.853,    1.853,    3.441, ],
                             [  -0.000,    2.333,    2.000, ],
                             [   3.150,    3.150,   -0.450, ],
                             [  -1.853,    0.000,    3.441, ],
                             [  -0.000,    0.000,    2.000, ],
                             [   3.150,    0.000,   -0.450, ],
                             [  -1.853,   -1.853,    3.441, ],
                             [  -0.000,   -2.333,    2.000, ],
                             [   3.150,   -3.150,   -0.450, ],
                             ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), c_rad)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_simple_camera_and_image_at_neg_1cm(self):
        camera_pixels_shape_yx = (3, 3)
        rad = 0.732815101787

        intersections_rad_mm = [(rad, 10)]
        i2p = self.setup_i2p(
            camera_sensor_size_mm_xy=(3, 3),
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            intersections_rad_mm=intersections_rad_mm,
            focal_length_mm=3.0,
            )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -2.432,    2.432,    1.703, ],
                             [   0.000,    3.333,   -1.000, ],
                             [   5.294,    5.294,   -6.882, ],
                             [  -2.432,    0.000,    1.703, ],
                             [   0.000,    0.000,   -1.000, ],
                             [   5.294,    0.000,   -6.882, ],
                             [  -2.432,   -2.432,    1.703, ],
                             [   0.000,   -3.333,   -1.000, ],
                             [   5.294,   -5.294,   -6.882, ],
                             ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), rad)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_simple_camera_and_image_at_neg_2cm(self):
        camera_pixels_shape_yx = (3, 3)
        rad = 0.685729510906

        intersections_rad_mm = [(rad, 11)]
        i2p = self.setup_i2p(
            camera_sensor_size_mm_xy=(3, 3),
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            intersections_rad_mm=intersections_rad_mm,
            focal_length_mm=3.0,
            )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -2.605,    2.605,    1.184, ],
                             [  -0.000,    3.667,   -2.000, ],
                             [   6.187,    6.187,   -9.562, ],
                             [  -2.605,    0.000,    1.184, ],
                             [  -0.000,    0.000,   -2.000, ],
                             [   6.187,    0.000,   -9.562, ],
                             [  -2.605,   -2.605,    1.184, ],
                             [  -0.000,   -3.667,   -2.000, ],
                             [   6.187,   -6.187,   -9.562, ],
                             ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), rad)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_alternate_camera_and_image_at_0cm(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            camera_sensor_size_mm_xy=(1.0, 1.0),
            focal_length_mm=2.0,
            intersections_rad_mm=[(np.pi / 4, 9)]
        )
        image = np.ones(camera_pixels_shape_yx).astype('bool')
        expected = np.array([[  -1.286,    1.286,    1.286, ],
                             [  -0.000,    1.500,    0.000, ],
                             [   1.800,    1.800,   -1.800, ],
                             [  -1.286,   -0.000,    1.286, ],
                             [  -0.000,   -0.000,    0.000, ],
                             [   1.800,   -0.000,   -1.800, ],
                             [  -1.286,   -1.286,    1.286, ],
                             [  -0.000,   -1.500,    0.000, ],
                             [   1.800,   -1.800,   -1.800, ],
                             ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_returns_expected_points_give_simple_camera_and_1_column(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx)
        image = np.zeros(camera_pixels_shape_yx).astype('bool')
        image[:, 0] = True

        expected = np.array([
            [-3.0,  3.0,  3.0],  # -1, -1
            [-3.0,  0.0,  3.0],  # -1,  0 
            [-3.0, -3.0,  3.0],  # -1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_should_rotate_at_45(self):
        camera_pixels_shape_yx = (3, 3)
        i2p = self.setup_i2p(
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            camera_sensor_size_mm_xy=(3.0, 3.0),
            focal_length_mm=3.0,
            intersections_rad_mm=[(np.pi / 4, 9)]
        )
        image = np.zeros(camera_pixels_shape_yx).astype('bool')
        image[1, 0] = 1

        r = sqrt(2.25 * 2.25 * 2)
        x = -2.250
        z = 2.250
        theta = atan(z / x)

        for i in range(0, 200):
            rotation = ((i / 200.0) * np.pi * 2)
            offset = rotation + theta
            nx = sin(offset) * r
            nz = cos(offset) * r

            expected = np.array([[nx,    0.000,   nz]], dtype='float16')
            result = i2p.get_points(image, rotation, ROI(0, 0, 1, 1), np.pi / 4)

            self.assert_array(expected, result, atol=1e-01)

    def test_get_points_should_roi(self):
        camera_pixels_shape_yx = (4, 4)
        i2p = self.setup_i2p(
            camera_pixels_shape_yx=camera_pixels_shape_yx, 
            camera_sensor_size_mm_xy=(4, 4),
            focal_length_mm=3.0,
            intersections_rad_mm=[(np.pi / 4, 9)]
            )
        image = np.ones((4, 4)).astype('bool')
        expected = np.array([
            [-1.286, 1.286, 1.286],  # -1, -1
            [ 1.800, 1.800,-1.800],  #  0, -1
            [-1.286,-1.286, 1.286],  # -1,  0 
            [ 1.800,-1.800,-1.800],  #  0,  0 
            ], dtype='float16')

        roi = ROI(.25, .25, 0.5, 0.5)

        result = i2p.get_points(image, 0, roi, np.pi / 4)

        self.assert_array(expected, result)

    def test_get_points_should_return_nothing_when_ray_and_plane_dont_intersect(self):
        camera_pixels_shape_yx = (4, 4)
        i2p = self.setup_i2p(camera_pixels_shape_yx=camera_pixels_shape_yx, camera_sensor_size_mm_xy=(20, 20))
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

    def test_get_points_returns_expected_points_give_real_camera_and_image_at_5cm(self):
        camera_pixels_shape_yx = (480, 640)
        intersections_rad = atan(175.0/125.0)
        i2p = self.setup_i2p(
            camera_pixels_shape_yx=camera_pixels_shape_yx,
            camera_sensor_size_mm_xy=(0.750, 0.562),
            focal_length_mm=1.0,
            focal_point_to_center_mm=175.0,
            intersections_rad_mm=[(intersections_rad, 125.0)]
        )
        image = np.zeros(camera_pixels_shape_yx).astype('bool')
        image[120, 160] = True
        image[120, 320] = True
        image[120, 480] = True
        image[240, 160] = True
        image[240, 320] = True
        image[240, 480] = True
        expected = np.array([[-20.612,   15.429,   64.723],
                             [  0.073,   17.497,   49.948],
                             [ 27.160,   20.204,   30.600],
                             [-20.612,   -0.065,   64.723],
                             [  0.073,   -0.073,   49.948],
                             [ 27.160,   -0.085,   30.600]], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1), intersections_rad)

        self.assert_array(expected, result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
