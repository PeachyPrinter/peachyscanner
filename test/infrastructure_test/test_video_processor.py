import unittest
import sys
import os
import logging
import time
import cv2 
import numpy as np
from mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpers import FakeCamera
from infrastructure.video_processor import VideoProcessor
from infrastructure.roi import ROI

class TestHandler(object):
    def __init__(self, unsubscribe_after=-1):
        self.unsubscribe_after = unsubscribe_after
        self.calls = []

    def handle(self, **kwargs):
        arg = {}
        self.calls.append({
            'frame':kwargs['frame'].copy(),
            'section': kwargs['section']})
        self.unsubscribe_after -= 1
        return self.unsubscribe_after != 0

class VideoProcessorTest(unittest.TestCase):
    def show_it(self, image):
        cv2.imshow('frame', image)

    def create_video_processor(self, roi=None):
        self.camera = FakeCamera()
        self.encoder = Mock()
        self.encoder.should_capture_frame_for_section.return_value = (True, 0)
        x_center = self.camera.image.shape[1] // 2
        if roi:
            self.roi = roi
        else:
            self.roi = ROI(10, 50, x_center + 1, 20, self.camera.image.shape)
        return VideoProcessor(self.camera, self.encoder, self.roi)
        
    def test_video_processor_starts_and_stops_given_shutdown_set_to_true(self):
        video_processor = self.create_video_processor()
        video_processor.start()
        self.assertTrue(video_processor.is_alive())
        video_processor.stop()
        self.assertFalse(video_processor.is_alive())

    def test_subscribe_adds_a_subscriber_which_is_called(self):
        video_processor = self.create_video_processor()
        handler = TestHandler()
        video_processor.subscribe(handler)
        video_processor.start()
        time.sleep(0.1)
        video_processor.stop()

        self.assertTrue(len(handler.calls) > 0)

    def test_handler_should_receive_frames_from_the_camera(self):
        video_processor = self.create_video_processor()
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(0.1)
        video_processor.stop()
        self.assertTrue((subscriber.calls[0]['frame'] == self.clipped_image()).all())

    def test_all_handlers_should_receive_same_frames_from_the_camera(self):
        video_processor = self.create_video_processor()
        subscriber1 = TestHandler()
        subscriber2 = TestHandler()
        video_processor.subscribe(subscriber1)
        video_processor.subscribe(subscriber2)
        video_processor.start()
        time.sleep(0.1)
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
        time.sleep(0.1)
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
        time.sleep(0.1)
        video_processor.stop()
        self.assertEquals(0, len(subscriber.calls))

    def test_handler_should_store_the_image_data_at_the_given_section(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (False, 0)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(0.1)
        video_processor.stop()
        self.assertEquals(0, len(subscriber.calls))

    def test_handler_should_be_given_the_section_when_called(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler()
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(0.1)
        video_processor.stop()
        self.assertTrue(len(subscriber.calls) > 0)
        self.assertEquals(44, subscriber.calls[0]['section'])

    def test_when_handler_returns_false_unsubscribe_them(self):
        video_processor = self.create_video_processor()
        self.encoder.should_capture_frame_for_section.return_value = (True, 44)
        subscriber = TestHandler(unsubscribe_after=1)
        video_processor.subscribe(subscriber)
        video_processor.start()
        time.sleep(0.1)
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
        time.sleep(0.1)
        video_processor.stop()
        self.assertEquals(subscriber, callback.call_args[0][0])

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
