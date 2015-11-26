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


class PointConverterTest(unittest.TestCase):

    def test_one_is_one(self):
        self.assertTrue(1 == 1)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
