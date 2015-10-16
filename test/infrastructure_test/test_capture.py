import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.detector import Detector
from infrastructure.roi import ROI
from infrastructure.capture import PointCapture, ImageCapture


class PointCaptureTest(unittest.TestCase):
    pass


class ImageCaptureTest(unittest.TestCase):
    pass

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
