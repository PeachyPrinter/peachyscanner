import unittest
import sys
import os
import logging
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mock import patch, Mock
from api.scanner import ScannerAPI
from infrastructure.roi import ROI
from infrastructure.data_capture import ImageCapture, PointCapture
from helpers import TestHelpers


class ScannerAPITest(TestHelpers):

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_from_abs_points_should_create_expected_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        expected_roi = ROI.set_from_abs_points((0, 0), (151, 90), [100, 300, 3])

        api.set_region_of_interest_from_abs_points((0, 0), (151, 90), [300, 100])

        self.assertROIEquals(expected_roi, api.roi)

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_from_abs_points_should_replace_the_roi_on_the_video_processor_with_new_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.set_region_of_interest_from_abs_points((0, 0), (151, 90), [300, 100])
        self.assertNotEquals(api._default_roi, api.video_processor.roi)
        self.assertEquals(api.roi, api.video_processor.roi)

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_rel_points_should_create_expected_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        expected_roi = ROI(0.0, 0.0, 0.5, 0.9)

        api.set_region_of_interest_from_rel_points(0, 0, 0.5, 0.9)

        self.assertROIEquals(expected_roi, api.roi)

    @patch('api.scanner.Camera')
    def test_set_region_of_interest_rel_points_should_replace_the_roi_on_the_video_processor_with_new_roi(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.set_region_of_interest_from_rel_points(0.0, 0.0, 0.5, 0.9)
        self.assertNotEquals(api._default_roi, api.video_processor.roi)
        self.assertEquals(api.roi, api.video_processor.roi)

    @patch('api.scanner.Camera')
    def test_configure_encoder_should_create_an_encoder_with_the_given_config(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_encoder((0.5, 0.5), 500, 100, 200)
        self.assertEquals((0.5, 0.5), api.encoder.relitive_point_xy)
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
    def test_configure_laser_detector_should_create_an_laser_detector_with_the_given_config(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector((0.0, 0.0, 0.0), (0.0, 0.0, 0.5))
        self.assertEquals((0, 0, 0), api.laser_detector.low_bgr)
        self.assertEquals((127, 0, 0), api.laser_detector.high_bgr)
        
    @patch('api.scanner.Camera')
    def test_configure_laser_detector_should_replace_the_existing_laser_detector_with_new_laser_detector(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector((0.0, 0.0, 0.0), (0.0, 0.0, 0.5))
        initial = api.laser_detector
        api.configure_laser_detector((0.5, 0.5, 0.5), (1.0, 1.0, 1.0))
        self.assertNotEquals(api.laser_detector, initial)

    @patch('api.scanner.Camera')
    def test_configure_laser_detector_should_replace_the_laser_detector_on_the_video_processor_with_new_laser_detector(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
        self.assertNotEquals(api._default_laser_detector, api.video_processor.laser_detector)
        self.assertEquals(api.laser_detector, api.video_processor.laser_detector)

    @patch('api.scanner.Camera')
    def test_configure_laser_detector_should_create_an_laser_detector_with_the_given_config(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector2(255, (3, 3), 'red')
        self.assertEquals(255, api.laser_detector.threshold)
        self.assertEquals((3, 3), api.laser_detector.filter_size_yx)
        self.assertEquals('red', api.laser_detector.color)

    @patch('api.scanner.Camera')
    def test_configure_laser_detector2_should_replace_the_existing_laser_detector_with_new_laser_detector(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector2(255, (3, 3), 'red')
        initial = api.laser_detector
        api.configure_laser_detector2(225, (5, 5), 'blue')
        self.assertNotEquals(api.laser_detector, initial)

    @patch('api.scanner.Camera')
    def test_configure_laser_detector2_should_replace_the_laser_detector_on_the_video_processor_with_new_laser_detector(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.configure_laser_detector2(255, (3, 3), 'red')
        self.assertNotEquals(api._default_laser_detector, api.video_processor.laser_detector)
        self.assertEquals(api.laser_detector, api.video_processor.laser_detector)

    @patch('api.scanner.Camera')
    def test_init_should_construct_a_video_processor(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        self.assertTrue(api.video_processor is not None)
        self.assertEquals(api._default_encoder, api.video_processor.encoder)
        self.assertEquals(api._default_roi, api.video_processor.roi)
        self.assertEquals(api._default_laser_detector, api.video_processor.laser_detector)

    @patch('api.scanner.Camera')
    def test_capture_image_should_create_an_image_handler_and_subscribe_it_to_video_processor(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.capture_image()
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertEquals(ImageCapture, type(api.video_processor.handlers[0][0]))
        self.assertTrue(hasattr(api.video_processor.handlers[0][0], 'handle'))

    @patch('api.scanner.Camera')
    def test_capture_image_should_subscribe_with_expected_callback(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        callback = Mock()
        api.capture_image(callback)
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertEquals(ImageCapture, type(api.video_processor.handlers[0][0]))
        self.assertEqual(api.video_processor.handlers[0][1], callback)


    @patch('api.scanner.Camera')
    def test_capture_image_should_subscribe_with_expected_offset(self, mock_camera):
        cam = mock_camera.return_value
        expected_offset = 10
        cam.shape = [300, 100]
        api = ScannerAPI()
        callback = Mock()
        api.capture_image(callback, expected_offset)
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertEquals(ImageCapture, type(api.video_processor.handlers[0][0]))
        self.assertEqual(api.video_processor.handlers[0][1], callback)
        self.assertEqual(api.video_processor.handlers[0][0].section_offset, expected_offset)


    @patch('api.scanner.Camera')
    def test_capture_points_should_create_an_image_handler_and_subscribe_it_to_video_processor(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        api.capture_points()
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertEquals(PointCapture, type(api.video_processor.handlers[0][0]))
        self.assertTrue(hasattr(api.video_processor.handlers[0][0], 'handle'))

    @patch('api.scanner.Camera')
    def test_capture_points_should_subscribe_with_expected_callback(self, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        api = ScannerAPI()
        callback = Mock()
        api.capture_points(callback)
        self.assertTrue(len(api.video_processor.handlers) > 0)
        self.assertEquals(PointCapture, type(api.video_processor.handlers[0][0]))
        self.assertEqual(api.video_processor.handlers[0][1], callback)

    @patch('api.scanner.Camera')
    @patch('api.scanner.VideoProcessor')
    def test_start_starts_the_camera_and_video_processor(self, mock_video_processor, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        video = mock_video_processor.return_value
        api = ScannerAPI()
        api.start()
        cam.start.assert_called_once_with()
        video.start.assert_called_once_with()

    @patch('api.scanner.Camera')
    @patch('api.scanner.VideoProcessor')
    def test_stop_stops_the_camera_and_video_processor(self, mock_video_processor, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        video = mock_video_processor.return_value
        api = ScannerAPI()
        api.start()
        api.stop()
        cam.stop.assert_called_once_with()
        video.stop.assert_called_once_with()

    @patch('api.scanner.Camera')
    @patch('api.scanner.VideoProcessor')
    def test_stop_stops_the_video_processor_first(self, mock_video_processor, mock_camera):
        global stop_time_camera
        global stop_time_video
        stop_time_camera = 0
        stop_time_video = 0

        def stop_camera():
            global stop_time_camera
            stop_time_camera = time.time()
            time.sleep(0.01)

        def stop_video():
            global stop_time_video
            stop_time_video = time.time()
            time.sleep(0.01)
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        cam.stop.side_effect = stop_camera
        video = mock_video_processor.return_value
        video.stop.side_effect = stop_video
        api = ScannerAPI()
        api.start()
        api.stop()
        self.assertTrue(stop_time_video < stop_time_camera, '{} !< {}'.format(stop_time_video, stop_time_camera))

    @patch('api.scanner.Camera')
    @patch('api.scanner.VideoProcessor')
    def test_start_starts_the_camera_first(self, mock_video_processor, mock_camera):
        global start_time_camera
        global start_time_video
        start_time_camera = 0
        start_time_video = 0

        def start_camera():
            global start_time_camera
            start_time_camera = time.time()
            time.sleep(0.01)

        def start_video():
            global start_time_video
            start_time_video = time.time()
            time.sleep(0.01)

        cam = mock_camera.return_value
        cam.shape = [300, 100]
        cam.start.side_effect = start_camera
        video = mock_video_processor.return_value
        video.start.side_effect = start_video
        api = ScannerAPI()
        api.start()
        self.assertTrue(start_time_video > start_time_camera, '{} !> {}'.format(start_time_video, start_time_camera))

    @patch('api.scanner.Camera')
    @patch('api.scanner.VideoProcessor')
    def test_get_feed_image_gets_image_from_feed(self, mock_video_processor, mock_camera):
        cam = mock_camera.return_value
        cam.shape = [300, 100]
        video = mock_video_processor.return_value
        video.get_bounded_image.return_value = 'Expected Image'
        api = ScannerAPI()
        result = api.get_feed_image((200, 100))
        self.assertEqual('Expected Image', result)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()