import unittest
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mock import patch
from api.scanner import ScannerAPI
from infrastructure.roi import ROI
from helpers import TestHelpers


class ScannerAPITest(TestHelpers):
    def test_capture_image_raises_exception_when_roi_not_specified(self):
        api = ScannerAPI()
        with self.assertRaises(Exception):
            api.capture_image()

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_should_create_expected_roi(self, mock_camera):
        api = ScannerAPI()
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        expected_roi = ROI.set_from_points((0, 0), (151, 90), [100, 300, 3])
        api.set_region_of_interest((0, 0), (151, 90))
        self.assertROIEquals(expected_roi, api.roi)

    @patch('api.scanner.Camera')
    def test_capture_image_raises_exception_when_encoder_not_specified(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.set_region_of_interest((0, 0), (151, 90))

        with self.assertRaises(Exception):
            api.capture_image()

    def test_configure_encoder_should_create_an_encoder_with_the_given_config(self):
        api = ScannerAPI()
        api.configure_encoder((50, 50), 500, 100, 200)
        self.assertEquals((50, 50), api.encoder.point)
        self.assertEquals(500, api.encoder.threshold)
        self.assertEquals(100, api.encoder.null_zone)
        self.assertEquals(200, api.encoder.sections)

    def test_configure_encoder_should_replace_the_existing_encoder_with_new_encoder(self):
        api = ScannerAPI()
        api.configure_encoder((50, 50), 500, 100, 200)
        initial = api.encoder
        api.configure_encoder((51, 51), 500, 100, 200)
        self.assertNotEquals(api.encoder, initial)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()