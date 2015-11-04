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
        expected_result = np.array([0, 1, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_2(self):
        data = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([0, 1, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_when_more_then_one(self):
        data = np.array([[1, 1, 1],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([0, 1, 0])

        result = self.test_converter.get_points(data,2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_0_for_missing_points_expected_array_when_none(self):
        data = np.array([[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]])
        expected_result = np.array([0, 0, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([2, 1, 0])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_0_when_points_beyond_center(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([0, 0, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_missing(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([2, 0, 0])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_extras(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 1, 1, 1, 1, 1]])
        expected_result = np.array([2, 1, 2])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_extras_unsorted(self):
        data = np.array([[0, 1, 0, 0, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 1, 0, 0, 0, 0, 0]])
        expected_result = np.array([3, 2, 1, 1, 2])

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
        expected = np.zeros((100, sections), dtype='uint8')
        expected[:, 0] = return_array

        point_capture = PointCapture(sections)
        result = point_capture.handle(detected=detected, section=0, roi_center_y=50)

        self.assertTrue(result)
        self.assertTrue((expected == point_capture.points).all())

    def test_handle_give_region_containing_data_returns_expected_point_in_simple_example(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((1, sections), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        result = point_capture.handle(detected=detected, section=0, roi_center_y=50)

        self.assertTrue(result)
        self.assertTrue((expected == point_capture.points).all())

    def test_after_handling_all_sections_should_return_0(self, mock_PointConverter):
        mock_point_converter = mock_PointConverter.return_value
        mock_point_converter.get_points.return_value = np.ones((1), dtype='uint32')
        sections = 200
        detected = np.zeros((1, 10, 1), dtype='uint8')
        detected[:][0] = 255
        expected = np.zeros((1, sections), dtype='uint8')
        expected[:, 0] = np.array([1])

        point_capture = PointCapture(sections)
        for idx in range(sections):
            result = point_capture.handle(detected=detected, section=idx, roi_center_y=50)

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
            result = point_capture.handle(detected=detected, section=index, roi_center_y=50)

        self.assertFalse(result)


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
        image_capture.handle(frame)

        self.assertTrue((image_capture.image[0] == expected[0]).all())

    def test_handle_should_store_the_slice_at_the_given_index(self):
        sections = 200
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        frame[:, -1] = (255, 0, 0)
        expected = np.zeros((100, sections, 3), dtype='uint8')
        expected[:, 20] = (255, 0, 0)
        image_capture = ImageCapture(sections)
        image_capture.handle(frame, 20)

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

        image_capture.handle(frame, 0)
        image_capture.handle(frame2, 1)

        self.assertTrue((image_capture.image == expected).all())

    def test_handle_should_return_false_given_all_sections_have_been_captured(self):
        sections = 5
        frame = np.ones((100, 130, 3), dtype='uint8') * 128
        image_capture = ImageCapture(sections)
        results = [image_capture.handle(frame, section) for section in range(5)]
        self.assertEquals(5, len(results))
        self.assertTrue(results[3])
        self.assertFalse(results[4])



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
