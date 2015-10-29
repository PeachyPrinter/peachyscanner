import unittest
import sys
import os
import numpy as np
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.detector import Detector
from infrastructure.roi import ROI
from infrastructure.point_converter import PointConverter

from mock import Mock

class DetectorTest(unittest.TestCase):
    def test_overlay_mask_returns_green_for_points_in_range(self):
        image = np.ones((5, 5, 3), dtype='uint8') * 200
        expected = np.ones((5, 5, 3), dtype='uint8') * 200
        image[1:4, 1:4] = (128, 128, 128)
        expected[1:4, 1:4] = (0, 255, 0)
        roi = ROI(0,0,1,1)
        detector = Detector(PointConverter())
        detector.process(image, roi)
        masked = detector.overlay_mask(image)
        self.assertTrue((expected == masked).all())

    def test_overlay_mask_returns_points_in_roi(self):
        image = np.ones((5, 5, 3), dtype='uint8') * 128
        expected = np.ones((5, 5, 3), dtype='uint8') * 128
        expected[1:4, 1:4] = (0, 255, 0)
        roi = ROI(1, 1, 3, 3)
        detector = Detector(PointConverter())
        detector.process(image, roi)
        masked = detector.overlay_mask(image)
        self.assertTrue((expected == masked).all())

    def test_overlay_mask_works_when_roi_changes(self):
        image = np.ones((5, 5, 3), dtype='uint8') * 128
        expected = np.ones((5, 5, 3), dtype='uint8') * 128
        expected[1:4, 1:4] = (0, 255, 0)
        roi = ROI(1, 1, 3, 3)
        detector = Detector(PointConverter())
        detector.process(image, roi)
        roi.w = 4
        detector.overlay_mask(image)

    def test_points_calls_point_converter(self):
        image = np.ones((10, 10, 3), dtype='uint8') * 128
        expected = np.ones((3, 3), dtype='uint8') * 255
        roi = ROI(1, 1, 3, 3)
        point_converter = Mock()
        point_converter.get_points.return_value = 'BeeBopWrrr'
        detector = Detector(point_converter)
        detector.process(image, roi)
        points = detector.points(image)
        self.assertTrue((expected == point_converter.get_points.call_args[0][0][0]).all())
        self.assertEquals(4, point_converter.get_points.call_args[0][1])
        self.assertEquals('BeeBopWrrr', points)



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()