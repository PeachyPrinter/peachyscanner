import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.image_2_points import Image2Points
from infrastructure.roi import ROI


class PointConverterTest(unittest.TestCase):

    def setup_i2p(self, camera_pixels_shape_xy=(3, 3), camera_sensor_size_mm=(13.5, 13.5),):
        return Image2Points(
            camera_focal_length_mm=9,
            camera_sensor_size_mm=camera_sensor_size_mm,
            camera_pixels_shape_xy=camera_pixels_shape_xy,
            laser_center_intersection_rad=np.pi / 4,
            center_intersection_xyz=(0, 0, -9),
            )

    def assert_array(self, array1, array2, rtol=1e-05):
        self.assertTrue(array1.shape == array2.shape)
        for idx in range(array1.shape[0]):
            self.assertTrue(np.allclose(array1[idx], array2[idx], rtol=rtol), "TEST:{}:  {} == {}".format(idx, array1[idx], array2[idx]))

    def test_get_points_returns_expected_points_give_simple_camera_and_image(self):
        camera_pixels_shape_xy = (3, 3)
        i2p = self.setup_i2p(camera_pixels_shape_xy=camera_pixels_shape_xy)
        image = np.ones(camera_pixels_shape_xy).astype('bool')
        expected = np.array([
            [-3.0, -3.0,  3.0],  # -1, -1
            [-3.0,  0.0,  3.0],  # -1,  0 
            [-3.0,  3.0,  3.0],  # -1,  1 
            [ 0,   -4.5,  0.0],  #  0, -1
            [ 0,    0.0,  0.0],  #  0,  0 
            [ 0,    4.5,  0.0],  #  0,  1 
            [ 9.0, -9.0, -9.0],  #  1, -1
            [ 9.0,    0, -9.0],  #  1,  0 
            [ 9.0,  9.0, -9.0],  #  1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1))

        self.assert_array(expected, result)

    def test_get_points_should_rotate(self):
        camera_pixels_shape_xy = (3, 3)
        rotation = np.pi / 2.0
        i2p = self.setup_i2p(camera_pixels_shape_xy=camera_pixels_shape_xy)
        image = np.ones(camera_pixels_shape_xy).astype('bool')
        expected = np.array([
            [3.0, -3.0,   3.0],  # -1, -1
            [3.0,  0.0,   3.0],  # -1,  0 
            [3.0,  3.0,   3.0],  # -1,  1 
            [ 0,   -4.5,  0.0],  #  0, -1
            [ 0,    0.0,  0.0],  #  0,  0 
            [ 0,    4.5,  0.0],  #  0,  1 
            [-9.0, -9.0, -9.0],  #  1, -1
            [-9.0,    0, -9.0],  #  1,  0 
            [-9.0,  9.0, -9.0],  #  1,  1 
            ], dtype='float16')

        result = i2p.get_points(image, rotation, ROI(0, 0, 1, 1))

        self.assert_array(expected, result, rtol=1e-03)

    def test_get_points_should_roi(self):
        camera_pixels_shape_xy = (4, 4)
        i2p = self.setup_i2p(camera_pixels_shape_xy=camera_pixels_shape_xy, camera_sensor_size_mm=(18,18))
        image = np.ones((2, 2)).astype('bool')
        expected = np.array([
            [-3.0, -3.0,   3.0],  # -1, -1
            [-3.0,  0.0,   3.0],  # -1,  0 
            [ 0,   -4.5,  0.0],  #  0, -1
            [ 0,    0.0,  0.0],  #  0,  0 
            ], dtype='float16')

        roi = ROI(.25, .25, 0.5, 0.5)

        result = i2p.get_points(image, 0, roi)

        self.assert_array(expected, result)

    def test_get_points_should_return_nothing_when_ray_and_plane_dont_intersect(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
