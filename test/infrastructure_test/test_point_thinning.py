import unittest
import sys
import os
import logging
import numpy as np
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.point_thinning import PointThinner

class PointThinnerTest(unittest.TestCase):
    def test_thin_removes_points_within_a_specified_distance_in_single_plane_percision_0(self):
        points = np.array([[1.0, 0.0, 0.0], [1.4, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0], ])
        expected = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [3.0, 0.0, 0.0]])
        percision = 0

        PT = PointThinner()
        result = PT.thin(points, percision)

        result.sort(axis=0)
        self.assertTrue(np.array_equal(result, expected))

    def test_thin_removes_points_within_a_specified_distance_in_single_plane_percision_2(self):
        points = np.array([[1.0, 0.0, 0.0], [1.001, 0.0, 0.0], [2.0, 0.0, 0.0], [2.01, 0.0, 0.0], ])
        expected = np.array([[1.0, 0.0, 0.0], [2.0, 0.0, 0.0], [2.01, 0.0, 0.0]])
        percision = 2

        PT = PointThinner()
        result = PT.thin(points, percision)

        result.sort(axis=0)
        self.assertTrue(np.array_equal(result, expected))

    def test_thin_thins_large_arrays(self):
        points = np.random.random([10000, 3]).astype('float16')
        PT = PointThinner()
        result = PT.thin(points, 0)
        self.assertEqual(len(result), 8)
        
        PT = PointThinner()
        result = PT.thin(points, 1)
        self.assertTrue(len(result) < 10000)

    def test_thin_thins_large_arrays_fast(self):
        points = np.random.random([1000000, 3]).astype('float16')
        PT = PointThinner()
        start = time.time()
        result = PT.thin(points, 2)
        end = time.time() - start

        self.assertLess(end, 1)
        


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
