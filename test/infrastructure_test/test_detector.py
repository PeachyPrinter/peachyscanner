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

class DetectorTest(unittest.TestCase):
    def test_overlay_mask_returns_green_for_points_in_range(self):
        image = np.ones((5, 5, 3), dtype='uint8') * 200
        expected = np.ones((5, 5, 3), dtype='uint8') * 200
        image[1:4, 1:4] = (128, 128, 128)
        expected[1:4, 1:4] = (0, 255, 0)
        detector = Detector(ROI(), PointConverter())
        detector.process(image)
        masked = detector.overlay_mask(image)
        print masked
        self.assertTrue((expected == masked).all())

    def test_overlay_mask_returns_points_in_roi(self):
        image = np.ones((5, 5, 3), dtype='uint8') * 128
        expected = np.ones((5, 5, 3), dtype='uint8') * 128
        expected[1:4, 1:4] = (0, 255, 0)
        roi = ROI(1, 1, 3, 3)
        detector = Detector(roi, PointConverter())
        detector.process(image)
        masked = detector.overlay_mask(image)
        self.assertTrue((expected == masked).all())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()