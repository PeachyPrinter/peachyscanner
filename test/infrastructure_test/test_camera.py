import unittest
import sys
import os
import logging
import time
import cv2 
import numpy as np
from mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.camera import Camera


@patch('infrastructure.camera.VideoCapture')
class CameraTest(unittest.TestCase):
    def test_read_should_raise_exception_when_camera_not_started(self, mock_video_capture):
        camera = Camera()
        with self.assertRaises(Exception):
            camera.read()

    def test_start_should_start_cv_videoCapture(self, mock_video_capture):
        camera = Camera()
        camera.start()
        mock_video_capture.assert_called_once_with()



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()