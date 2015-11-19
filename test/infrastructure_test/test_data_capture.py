import unittest
import sys
import os
import numpy as np
import logging

from mock import Mock, patch
import cv2


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.data_capture import PointCapture, ImageCapture, PointConverter
from helpers import FakeCamera


class PointConverterTest(unittest.TestCase):
    def setUp(self):
        self.test_converter = PointConverter()

    def test_get_points_returns_expected_array(self):
        data = np.array([[0, 0, 1],
                         [0, 1, 0],
                         [1, 0, 0]])

        expected_result = np.array([0, 1, 2])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_2(self):
        data = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([2., 1., 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_when_more_then_one(self):
        data = np.array([[1, 1, 1],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([0, 1, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_0_for_missing_points_expected_array_when_none(self):
        data = np.array([[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]])
        expected_result = np.array([0, 0, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_average_for_missing_points_expected_array_when_none(self):
        data = np.array([[0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 0, 0, 0, 0, 0, 0, 0]])
        expected_result = np.array([2, 3, 4, 5, 6 ,7])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_average_for_missing_points_expected_array_when_none_at_end(self):
        data = np.array([[0, 0, 0, 0, 0, 1, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0]])
        expected_result = np.array([2, 3, 4, 0, 0 ,0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))


    def test_get_points_returns_average_for_missing_points_expected_array_when_none_at_start(self):
        data = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [1, 0, 0, 0, 0, 0, 0, 0]])
        expected_result = np.array([0, 0, 4, 5, 6 ,7])


    def test_get_points_returns_offset_points_when_centered(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([4, 3, 2])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_missing(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([4, 3, 2])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_extras(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 1, 1, 1, 1, 1]])
        expected_result = np.array([4, 3, 0])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_extras_unsorted(self):
        data = np.array([[0, 1, 0, 0, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, 0, 0, 0]])
        expected_result = np.array([6, 5, 4, 4, 5])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

@patch('infrastructure.data_capture.PointConverter')
class PointCaptureTest(unittest.TestCase):
    def test_handle_give_region_containing_no_data_returns_no_points(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        return_array = np.ones((100), dtype='uint32')
        mock_point_converter.get_points.return_value = return_array
        sections = 200
        detected = np.zeros((100, 130, 1), dtype='uint8')
        expected = np.zeros((sections, 100), dtype='uint8')
        expected[0] = return_array

        point_capture = PointCapture(sections)
        result = point_capture.handle(laser_detection=detected, section=0, roi_center_y=50)

        self.assertTrue(result)
        self.assertTrue((expected == point_capture.points_tyr).all())

    def test_handle_give_region_containing_data_returns_expected_point_in_simple_example(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((sections, 1), dtype='uint8')
        expected[0] = np.array([1])

        point_capture = PointCapture(sections)
        result = point_capture.handle(laser_detection=detected, section=0, roi_center_y=50)

        self.assertTrue(result)
        self.assertTrue((expected == point_capture.points_tyr).all())

    def test_after_handling_all_sections_should_return_0(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((sections, 1), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        for idx in range(sections):
            result = point_capture.handle(laser_detection=detected, section=idx, roi_center_y=50)

        self.assertFalse(result)

    def test_should_handle_all_sections_if_starting_at_not_0_index(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((1, sections), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        for idx in range(sections):
            index = (idx + 50) % 200
            result = point_capture.handle(laser_detection=detected, section=index, roi_center_y=50)

        self.assertFalse(result)

    def test_complete_should_be_false_if_all_sections_unhandled(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((1, sections), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        for idx in range(sections - 2):
            point_capture.handle(laser_detection=detected, section=idx, roi_center_y=50)

        self.assertFalse(point_capture.complete)

    def test_complete_should_be_true_if_all_sections_handled(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((1, sections), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        for idx in range(sections):
            point_capture.handle(laser_detection=detected, section=idx, roi_center_y=50)

        self.assertTrue(point_capture.complete)

    def test_status_should_return_amount_complete(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 10
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255

        point_capture = PointCapture(sections)
        for idx in range(sections):
            self.assertEquals(idx / float(sections), point_capture.status)
            point_capture.handle(laser_detection=detected, section=idx, roi_center_y=50)
        self.assertEquals(1.0, point_capture.status)


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

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
