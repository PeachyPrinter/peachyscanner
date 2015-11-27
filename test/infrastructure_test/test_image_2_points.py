import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock, patch
import cv2


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.image_2_points import Image2Points
from infrastructure.roi import ROI


class PointConverterTest(unittest.TestCase):

    def test_get_points_returns_expected_points_give_simple_camera_and_image(self):
        camera_pixels_shape_xy = (3, 3)
        i2p = Image2Points(
            camera_focal_length_mm=9,
            camera_sensor_size_mm=(13.5, 13.5),
            camera_pixels_shape_xy=camera_pixels_shape_xy,
            laser_center_intersection_rad=np.pi / 4,
            center_intersection_xyz=(0, 0, -9),
            )
        image = np.ones(camera_pixels_shape_xy).astype('bool')
        expected = np.array([
            [-3.0, -3.0,  -6.0],  # -1, -1
            [-3.0,  0.0,  -6.0],  # -1,  0 
            [-3.0,  3.0,  -6.0],  # -1,  1 
            [ 0,   -4.5,  -9.0],  #  0, -1
            [ 0,    0.0,  -9.0],  #  0,  0 
            [ 0,    4.5,  -9.0],  #  0,  1 
            [ 9.0, -9.0, -18.0],  #  1, -1
            [ 9.0,    0, -18.0],  #  1,  0 
            [ 9.0,  9.0, -18.0],  #  1,  1 
            ], dtype='float16')
        
        result = i2p.get_points(image, 0, ROI(0, 0, 1, 1))

        for idx in range(9):
            print "TEST:{}:  {} == {}".format(idx, expected[idx], result[idx])
            self.assertTrue(np.allclose(expected[idx], result[idx]))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
