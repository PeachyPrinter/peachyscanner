import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock, patch
import cv2


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.data_capture import ImageCapture, PointCaptureXYZ
from infrastructure.roi import ROI
from helpers import FakeCamera

class ImageCaptureTest(unittest.TestCase):
    def show_it(self, image):
        print(image)
        while True:
            cv2.imshow('frame', image)
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                break

    def test_handle_given_a_frame_should_store_the_right_edge(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame[:, -1] = (255, 0, 0)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 0] = (255, 0, 0)
        image_capture = ImageCapture(sections)
        image_capture.handle(frame=frame)

        self.assertTrue((image_capture.image[0] == expected[0]).all())

    def test_handle_should_store_the_slice_at_the_given_index(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame[:, -1] = (255, 0, 0)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 20] = (255, 0, 0)
        image_capture = ImageCapture(sections)
        image_capture.handle(frame=frame, section=20)

        self.assertTrue((image_capture.image == expected).all())

    def test_handle_should_return_expected_image_when_called_multiple_times(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame2 = frame.copy()
        frame[:, -1] = (255, 0, 0)
        frame2[:, -1] = (0, 0, 255)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 0] = (255, 0, 0)
        expected[:, 1] = (0, 0, 255)
        image_capture = ImageCapture(sections)

        image_capture.handle(frame=frame, section=0)
        image_capture.handle(frame=frame2, section=1)

        self.assertTrue((image_capture.image == expected).all())

    def test_handle_should_return_expected_image_when_offset_provided(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame2 = frame.copy()
        frame[:, -1] = (255, 0, 0)
        frame2[:, -1] = (0, 0, 255)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 100] = (255, 0, 0)
        expected[:, 101] = (0, 0, 255)
        image_capture = ImageCapture(sections, section_offset = 100)

        image_capture.handle(frame=frame, section=0)
        image_capture.handle(frame=frame2, section=1)

        self.assertTrue((image_capture.image == expected).all())

    def test_handle_should_return_expected_image_when_offset_provided_and_would_be_out_of_bounds(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame2 = frame.copy()
        frame[:, -1] = (255, 0, 0)
        frame2[:, -1] = (0, 0, 255)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 199] = (255, 0, 0)
        expected[:, 0] = (0, 0, 255)
        image_capture = ImageCapture(sections, section_offset = 199)

        image_capture.handle(frame=frame, section=0)
        image_capture.handle(frame=frame2, section=1)

        self.assertTrue((image_capture.image == expected).all())

    def test_handle_should_return_false_given_all_sections_have_been_captured(self):
        sections = 5
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)
        results = [image_capture.handle(frame=frame, section=section) for section in range(5)]
        self.assertEquals(5, len(results))
        self.assertTrue(results[3])
        self.assertFalse(results[4])

    def test_complete_should_be_false_before_all_sections_have_been_captured(self):
        sections = 5
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)
        [image_capture.handle(frame=frame, section=section) for section in range(4)]

        self.assertFalse(image_capture.complete)

    def test_complete_should_be_true_when_all_sections_have_been_captured(self):
        sections = 5
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)

        [image_capture.handle(frame=frame, section=section) for section in range(5)]

        self.assertTrue(image_capture.complete)

    def test_handle_can_handle_erronous_keywords(self):
        sections = 5
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)

        [image_capture.handle(frame=frame, section=section, kitten='bohahaha') for section in range(5)]

        self.assertTrue(image_capture.complete)

    def test_status_should_return_amount_complete(self):
        sections = 10
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)

        for idx in range(sections):
            self.assertEquals(idx / float(sections), image_capture.status)
            image_capture.handle(frame=frame, section=idx, kitten='bohahaha')
        self.assertEquals(1.0, image_capture.status)


   # def test_camera_displays_image(self):
   #     camera = FakeCamera()
   #     while True:
   #         cv2.imshow('frame', camera.read())
   #         key = chr(cv2.waitKey(1) & 0xFF)
   #         if key == 'q':
   #             break

class PointCaptureXYZTest(unittest.TestCase):

    def setUp(self):
        self.img2point = Mock()
        self.img2point.get_points.return_value = np.array([1.0, 1.0, 1.0])
        self.roi = ROI(0, 0, 1, 1)
        self.laser_theta = 77

    def test_should_handle_all_sections_if_starting_at_not_0_index(self):
        sections = 200
        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        for idx in range(sections):
            index = (idx + 50) % 200
            result = point_capture.handle(laser_detection="BLA", section=idx, roi=self.roi)

        self.assertFalse(result)

    def test_complete_should_be_false_if_all_sections_unhandled(self):
        sections = 200
        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        for idx in range(sections - 2):
            point_capture.handle(laser_detection="BLA", section=idx, roi=self.roi)

        self.assertFalse(point_capture.complete)

    def test_complete_should_be_true_if_all_sections_handled(self):
        sections = 200

        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        for idx in range(sections):
            point_capture.handle(laser_detection="BLA", section=idx, roi=self.roi)

        self.assertTrue(point_capture.complete)

    def test_status_should_return_amount_complete(self):
        sections = 10

        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        for idx in range(sections):
            self.assertEquals(idx / float(sections), point_capture.status)
            point_capture.handle(laser_detection="BLA", section=idx, roi=self.roi)
        self.assertEquals(1.0, point_capture.status)

    def test_handle_ignores_extra_keywords(self):
        point_capture = PointCaptureXYZ(10, self.img2point, self.laser_theta)
        point_capture.handle(frame='pizza', laser_detection="BLA", section=0, roi=self.roi)

    def test_handle_calls_img2points(self):
        sections = 200
        frame = np.ones((200,200), dtype='uint8')
        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)

        point_capture.handle(laser_detection=frame, section=0, roi=self.roi)

        self.img2point.get_points.assert_called_with(frame, 0, self.roi, self.laser_theta)


    def test_handle_calls_img2points_with_correct_rad(self):
        sections = 200
        current_section = 50
        expected_rad = np.pi / 2.0
        frame = np.ones((200, 200), dtype='uint8')
        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)

        point_capture.handle(laser_detection=frame, section=current_section, roi=self.roi)

        self.img2point.get_points.assert_called_with(frame, expected_rad, self.roi, self.laser_theta)


    def test_handle_stores_points(self):
        sections = 200
        frame = np.ones((200, 200), dtype='uint8')
        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        expected = np.array([[1.0, 1.0, 1.0]])

        point_capture.handle(laser_detection=frame, section=0, roi=self.roi)

        actual = point_capture.points_xyz

        self.assertTrue((expected == actual).all())

    def test_handle_stores_points_more_then_once(self):
        sections = 4
        frame = np.ones((200, 200), dtype='uint8')

        self.img2point = Mock()
        points = [np.array([[1.0, 1.0, 1.0]], dtype='float16'), np.array([[2.0, 2.0, 2.0]], dtype='float16')]

        self.img2point.get_points.side_effect = points

        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta)
        expected = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])

        point_capture.handle(laser_detection=frame, section=0, roi=self.roi)
        point_capture.handle(laser_detection=frame, section=1, roi=self.roi)

        actual = point_capture.points_xyz

        self.assertTrue((expected == actual).all())

    def test_handle_adds_to_existing_points(self):
        sections = 4
        frame = np.ones((200, 200), dtype='uint8')

        self.img2point = Mock()
        points = [np.array([[1.0, 1.0, 1.0]], dtype='float16'), np.array([[2.0, 2.0, 2.0]], dtype='float16')]

        self.img2point.get_points.side_effect = points

        point_capture = PointCaptureXYZ(sections, self.img2point, self.laser_theta, points_xyz=np.array([[-1.0, -1.0, -1.0], [-2.0, -2.0, -2.0]]))
        expected = np.array([[-1.0, -1.0, -1.0], [-2.0, -2.0, -2.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])

        point_capture.handle(laser_detection=frame, section=0, roi=self.roi)
        point_capture.handle(laser_detection=frame, section=1, roi=self.roi)

        actual = point_capture.points_xyz

        self.assertEquals(expected.shape, actual.shape)
        self.assertTrue((expected == actual).all())

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
