import unittest
import sys
import os
import logging
import time
import cv2
from mock import Mock
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpers import FakeCamera
from infrastructure.video_processor import VideoProcessor
from infrastructure.roi import ROI
from infrastructure.laser_detector import LaserDetector

class TestHandler(object):
    def __init__(self, unsubscribe_after=-1):
        self.unsubscribe_after = unsubscribe_after
        self.calls = []

    def handle(self, **kwargs):
        self.calls.append({
            'frame': kwargs['frame'].copy(),
            'section': kwargs['section'],
            'roi_center_y': kwargs['roi_center_y'],
            'laser_detection': kwargs['laser_detection'],
            })
        self.unsubscribe_after -= 1
        return self.unsubscribe_after != 0

class VideoProcessorTest(unittest.TestCase):
    start_up_delay = 0.005
    def show_it(self, image):
        cv2.imshow('frame', image)

    def create_video_processor(self, roi=None):
        self.camera = FakeCamera()
        self.encoder = Mock()
        self.encoder.should_capture_frame_for_section.return_value = (True, 0)
        self.mock_laser_detector = Mock()
        self.detected_image = np.ones((self.camera.image.shape[0], self.camera.image.shape[1]), dtype='uint8') * 255
        self.mock_laser_detector.detect.return_value = self.detected_image
        x_center = self.camera.image.shape[1] // 2
        if roi:
            self.roi = roi
        else:
            self.roi = ROI.set_from_abs_points((10, 50), (x_center + 1, 70), self.camera.image.shape)
        return VideoProcessor(self.camera, self.encoder, self.roi, self.mock_laser_detector)

    def test_video_processor_starts_and_stops_given_shutdown_set_to_true(self):
        video_processor = self.create_video_processor()
        video_processor.start()
        time.sleep(self.start_up_delay) # wait for loop to start
        self.assertTrue(video_processor.is_alive())
        video_processor.stop()
        self.assertFalse(video_processor.is_alive())


    def test_subscribe_adds_a_subscriber_which_is_called(self):
        video_processor = self.create_video_processor()
        handler = TestHandler()
        video_processor.subscribe(handler)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()

        self.assertTrue(len(handler.calls) > 0)

    def test_handler_should_receive_frames_from_the_camera(self):
        video_processor = self.create_video_processor()
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertTrue((subscriber.calls[0]['frame'] == self.clipped_image()).all())

    def test_all_handlers_should_receive_same_frames_from_the_camera(self):
        video_processor = self.create_video_processor()
        subscriber1 = TestHandler()
        subscriber2 = TestHandler()
        video_processor.subscribe(subscriber1)
        video_processor.subscribe(subscriber2)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        clipped_image = self.clipped_image()

        self.assertTrue((subscriber1.calls[-1]['frame'] == subscriber1.calls[-1]['frame']).all())
        self.assertTrue((subscriber1.calls[-1]['frame'] == clipped_image).all())
        self.assertTrue((subscriber2.calls[-1]['frame'] == clipped_image).all())

    def test_handler_is_called_with_only_specified_region_of_frame(self):
        video_processor = self.create_video_processor()
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        x_center = self.camera.image.shape[1] // 2
        actual = subscriber.calls[0]['frame']
        expected = self.camera.image[50:70, 10:x_center]
        self.assertEquals(expected.shape, actual.shape)
        self.assertTrue((actual == expected).all())

    def test_handler_is_only_called_when_encoder_decides(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (False, 0)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertEquals(0, len(subscriber.calls))

    def test_handler_should_store_the_image_data_at_the_given_section(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (False, 0)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertEquals(0, len(subscriber.calls))

    def test_handler_should_be_given_the_section_when_called(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertTrue(len(subscriber.calls) > 0)
        self.assertEquals(44, subscriber.calls[0]['section'])

    def test_handler_should_be_given_the_center_of_roi_when_called(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertTrue(len(subscriber.calls) > 0)
        y_center = self.camera.image.shape[0] // 2
        y_offset = video_processor.roi.y_rel * self.camera.image.shape[0]
        roi_y_center = y_center - y_offset
        self.assertEquals(roi_y_center, subscriber.calls[0]['roi_center_y'])


    def test_handler_should_be_given_the_detected_laser(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        expected = self.roi.get_left_of_center(self.detected_image)

        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertTrue(len(subscriber.calls) > 0)
        self.assertTrue((expected == subscriber.calls[0]['laser_detection']).all())

    def test_when_handler_returns_false_unsubscribe_them(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler(unsubscribe_after=1)
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertEquals(len(subscriber.calls), 1)
        self.assertFalse(subscriber in video_processor.handlers)

    def test_subscribe_with_callback_calls_callback_with_handler(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler()
        callback = Mock()
        video_processor.subscribe(subscriber, callback)
        video_processor.start()
        time.sleep(self.start_up_delay)
        video_processor.stop()
        self.assertEquals(subscriber, callback.call_args[0][0])

    def test_image_is_a_one_pixel_frame_when_called_before_started(self):
        video_processor = self.create_video_processor()
        self.assertEqual((1, 1, 3), video_processor.image['frame'].shape)

    def test_get_bounded_image_gets_a_scaled_version_of_the_lastest_frame(self):
        video_processor = self.create_video_processor()
        expected_x = 400
        expected_y = int(self.camera.image.shape[0] * float(expected_x) / self.camera.image.shape[1])

        video_processor.start()
        time.sleep(self.start_up_delay)
        image = video_processor.get_bounded_image(400, 200)
        video_processor.stop()

        self.assertEquals(expected_x, image['frame'].shape[1])
        self.assertEquals(expected_y, image['frame'].shape[0])

    def test_get_bounded_image_gets_a_scaled_version_of_the_lastest_encoder_mask(self):
        video_processor = self.create_video_processor()
        self.encoder.overlay_encoder.return_value = 'KAWABUNGA'
        video_processor.start()
        time.sleep(self.start_up_delay)
        image = video_processor.get_bounded_image(400, 200)
        video_processor.stop()

        self.assertEquals('KAWABUNGA', image['encoder'])

    def test_get_bounded_image_gets_a_scaled_version_of_the_lastest_encoder_history(self):
        video_processor = self.create_video_processor()
        self.encoder.overlay_history.return_value = 'KAWABUNGA'
        video_processor.start()
        time.sleep(self.start_up_delay)
        image = video_processor.get_bounded_image(400, 200)
        video_processor.stop()

        self.assertEquals('KAWABUNGA', image['history'])

    def test_get_bounded_image_gets_a_scaled_version_of_the_roi_highlighted_image(self):
        mock_roi = Mock()
        video_processor = self.create_video_processor(roi=mock_roi)
        mock_roi.overlay.return_value = 'KAWABUNGA'
        video_processor.start()
        time.sleep(self.start_up_delay)
        image = video_processor.get_bounded_image(400, 200)
        video_processor.stop()

        self.assertEquals('KAWABUNGA', image['roi_frame'])

    def test_get_bounded_image_gets_a_scaled_version_of_the_color_match_mask(self):
        video_processor = self.create_video_processor()
        video_processor.start()
        time.sleep(self.start_up_delay)
        image = video_processor.get_bounded_image(400, 200)
        video_processor.stop()

        self.assertTrue((image['laser_detection'] == 255).all())

    # def test_make_it_go(self):
    #     camera = FakeCamera()
    #     while(True):
    #         self.show_it(camera.read())
    #         key = chr(cv2.waitKey(1) & 0xFF)
    #         if key == 'q':
    #             break
    #     cv2.destroyAllWindows()


    def clipped_image(self):
        return self.roi.get_left_of_center(self.camera.image)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()