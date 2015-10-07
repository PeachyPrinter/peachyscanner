import unittest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.point_converter import PointConverter


class PointConverterTest(unittest.TestCase):
    def setUp(self):
        self.test_converter = PointConverter()

    def test_get_points_returns_expected_array(self):
        data = np.array([[0, 0, 1],
                         [0, 1, 0],
                         [1, 0, 0]])
        expected_result = np.array([0, 1, -1])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_2(self):
        data = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([-1, 1, 0])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_expected_array_when_more_then_one(self):
        data = np.array([[1, 1, 1],
                         [0, 1, 0],
                         [0, 0, 1]])
        expected_result = np.array([-1, 1, 0])

        result = self.test_converter.get_points(data,2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_0_for_missing_points_expected_array_when_none(self):
        data = np.array([[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]])
        expected_result = np.array([-1, -1, -1])

        result = self.test_converter.get_points(data, 2)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 1, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([2, 1, 0])

        result = self.test_converter.get_points(data, 4)

        self.assertTrue((expected_result == result).all(), str(result))

    def test_get_points_returns_offset_points_when_centered_and_missing(self):
        data = np.array([[0, 0, 1, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 1, 0, 0]])
        expected_result = np.array([2, -1, 0])

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

if __name__ == '__main__':
    unittest.main()