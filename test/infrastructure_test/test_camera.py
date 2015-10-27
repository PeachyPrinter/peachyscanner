import unittest
import sys
import os
import logging
import time
import cv2 
import numpy as np
from mock import Mock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.camera import Camera


@patch('infrastructure.camera.VideoCapture')
class CameraTest(unittest.TestCase):
    def test_read_should_raise_exception_when_camera_not_started(self, mock_VideoCapture):
        camera = Camera()
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)
        with self.assertRaises(Exception):
            camera.read()

    def test_start_should_start_cv_videoCapture(self, mock_VideoCapture):
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)
        camera.start()
        mock_VideoCapture.assert_called_once_with(0)

    def test_stop_should_stop_cv_videoCapture(self, mock_VideoCapture):
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)
        camera.start()
        camera.stop()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.release.assert_called_once_with()

    def test_read_should_return_image_when_camera_running(self, mock_VideoCapture):
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)

        camera.start()
        actual_image = camera.read()
        camera.stop()

        self.assertEqual(expected_image, actual_image)

    def test_shape_returns_frame_shape_when_camera_running(self, mock_VideoCapture):
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)

        camera.start()
        actual_image_shape = camera.shape
        camera.stop()

        self.assertEqual((10, 20, 3), actual_image_shape)

    def test_shape_raises_exception_if_camera_not_started(self, mock_VideoCapture):
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        camera = Camera()
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.read.return_value = (True, expected_image)
        with self.assertRaises(Exception):
            camera.shape

    def test_get_settings_raises_exception_if_camera_not_started(self, mock_VideoCapture):
        camera = Camera()
        with self.assertRaises(Exception):
            camera.get_settings()

    def test_get_setting_should_returns_dict_of_settings_when_started(self, mock_VideoCapture):
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.get.return_value = 1.0
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        mock_video_capture.read.return_value = (True, expected_image)
        expected = [
                {'name': 'Brightness',      'value': 1.0, },
                {'name': 'Contrast',        'value': 1.0, },
                {'name': 'Saturation',      'value': 1.0, },
                {'name': 'Hue',             'value': 1.0, },
                {'name': 'Gain',            'value': 1.0, },
                {'name': 'Exposure',        'value': 1.0, },
            ]

        camera = Camera()
        camera.start()
        results = camera.get_settings()

        self.assertListEqual(expected, results)

    def test_get_settings_should_exclude_dict_settings_when_less_then_0(self, mock_VideoCapture):
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.get.return_value = -1.0
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        mock_video_capture.read.return_value = (True, expected_image)
        expected = []

        camera = Camera()
        camera.start()
        results = camera.get_settings()

        self.assertListEqual(expected, results)

    def test_set_setting_should_raise_exception_if_camera_not_started(self, mock_VideoCapture):
        camera = Camera()
        with self.assertRaises(Exception):
            camera.set_setting('Hue', '1.0')

    def test_set_setting_should_set_setting(self, mock_VideoCapture):
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.get.return_value = 1.0
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        mock_video_capture.read.return_value = (True, expected_image)

        camera = Camera()
        camera.start()
        results = camera.set_setting('Hue', 1.0)

        mock_video_capture.set.assert_called_once_with(cv2.CAP_PROP_HUE, 1.0)

    def test_set_setting_should_raise_exception_if_setting_not_in_list(self, mock_VideoCapture):
        mock_video_capture = mock_VideoCapture.return_value
        mock_video_capture.get.return_value = 1.0
        expected_image = Mock()
        expected_image.shape = (10, 20, 3)
        mock_video_capture.read.return_value = (True, expected_image)

        camera = Camera()
        camera.start()
        with self.assertRaises(Exception):
            camera.set_setting('Pizza', 1.0)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()