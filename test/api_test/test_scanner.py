import unittest
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mock import patch, Mock
from api.scanner import ScannerAPI
from infrastructure.roi import ROI
from infrastructure.data_capture import ImageCapture
from helpers import TestHelpers


class ScannerAPITest(TestHelpers):

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_should_create_expected_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        expected_roi = ROI.set_from_points((0, 0), (151, 90), [100, 300, 3])
        api.set_region_of_interest((0, 0), (151, 90))
        self.assertROIEquals(expected_roi, api.roi)

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_should_replace_the_roi_on_the_video_processor_with_new_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.set_region_of_interest((0, 0), (151, 90))
        self.assertNotEquals(api._default_roi, api.video_processor.roi)
        self.assertEquals(api.roi, api.video_processor.roi)

    @patch('api.scanner.Camera')
    def test_configure_encoder_should_create_an_encoder_with_the_given_config(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_encoder((50, 50), 500, 100, 200)
        self.assertEquals((50, 50), api.encoder.point)
        self.assertEquals(500, api.encoder.threshold)
        self.assertEquals(100, api.encoder.null_zone)
        self.assertEquals(200, api.encoder.sections)

    @patch('api.scanner.Camera')
    def test_configure_encoder_should_replace_the_existing_encoder_with_new_encoder(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_encoder((50, 50), 500, 100, 200)
        initial = api.encoder
        api.configure_encoder((51, 51), 500, 100, 200)
        self.assertNotEquals(api.encoder, initial)

    @patch('api.scanner.Camera')
    def test_configure_encoder_should_replace_the_encoder_on_the_video_processor_with_new_encoder(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_encoder((50, 50), 500, 100, 200)
        self.assertNotEquals(api._default_encoder, api.video_processor.encoder)
        self.assertEquals(api.encoder, api.video_processor.encoder)

    @patch('api.scanner.Camera')
    def test_init_should_construct_a_video_processor(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        self.assertTrue(api.video_processor is not None)
        self.assertEquals(api._default_encoder, api.video_processor.encoder)
        self.assertEquals(api._default_roi, api.video_processor.roi)

    @patch('api.scanner.Camera')
    def test_capture_image_should_create_an_image_handler_and_subscribe_it_to_video_processor(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        callback = Mock()
        api.capture_image(callback)
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertTrue(hasattr(api.video_processor.handlers[0], 'handle'))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()