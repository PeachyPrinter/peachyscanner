import unittest
import sys
import os
import numpy as np
import logging
import time


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from helpers import TestHelpers
from infrastructure.point_converter import GLConverter


class GLConverterTest(TestHelpers):

    def test_convert_returns_empty_for_empty_array(self):
        result = GLConverter().convert(np.array([]))
        self.assertEqual(0, len(result))

    def test_convert_returns_correct_X_Y_Z_for_simple_array(self):
        test_array = np.array([[9, 8], [7, 6], [5, 4], [3, 2]])
        result = GLConverter().convert(test_array)
        self.assertEqual(8 * 8, len(result))
        self.assertListAlmostEqual([ 9,  0, 0], result[0:3])
        self.assertListAlmostEqual([ 8,  0, 1], result[8:11])
        self.assertListAlmostEqual([ 0,  7, 0], result[16:19])
        self.assertListAlmostEqual([ 0,  6, 1], result[24:27])
        self.assertListAlmostEqual([-5,  0, 0], result[32:35])
        self.assertListAlmostEqual([-4,  0, 1], result[40:43])
        self.assertListAlmostEqual([ 0, -3, 0], result[48:51])
        self.assertListAlmostEqual([ 0, -2, 1], result[56:59])


    def test_convert_returns_correct_X_Y_Z_for_simple_array_with_scale(self):
        test_array = np.array([[9, 8], [7, 6], [5, 4], [3, 2]])
        result = GLConverter().convert(test_array, scale = 0.1)
        self.assertEqual(8 * 8, len(result))
        self.assertListAlmostEqual([ 0.9,  0.0, 0.0], result[0:3])
        self.assertListAlmostEqual([ 0.8,  0.0, 0.1], result[8:11])
        self.assertListAlmostEqual([ 0.0,  0.7, 0.0], result[16:19])
        self.assertListAlmostEqual([ 0.0,  0.6, 0.1], result[24:27])
        self.assertListAlmostEqual([-0.5,  0.0, 0.0], result[32:35])
        self.assertListAlmostEqual([-0.4,  0.0, 0.1], result[40:43])
        self.assertListAlmostEqual([ 0.0, -0.3, 0.0], result[48:51])
        self.assertListAlmostEqual([ 0.0, -0.2, 0.1], result[56:59])


    def test_convert_calculates_simple_normals(self):
        test_array = np.array([[9, 8], [7, 6], [5, 4], [3, 2]])
        result = GLConverter().convert(test_array)
        self.assertEqual(8 * 8, len(result))
        self.assertListAlmostEqual([ 1,  0, 0], result[3:][:3])
        self.assertListAlmostEqual([ 1,  0, 0], result[11:][:3])
        self.assertListAlmostEqual([ 0,  1, 0], result[19:][:3])
        self.assertListAlmostEqual([ 0,  1, 0], result[27:][:3])
        self.assertListAlmostEqual([-1,  0, 0], result[35:][:3])
        self.assertListAlmostEqual([-1,  0, 0], result[43:][:3])
        self.assertListAlmostEqual([ 0, -1, 0], result[51:][:3])
        self.assertListAlmostEqual([ 0, -1, 0], result[59:][:3])

    def test_convert_calculates_texture_coordanates(self):
        test_array = np.array([[9, 8], [7, 6], [5, 4], [3, 2]])
        result = GLConverter().convert(test_array)
        self.assertEqual(8 * 8, len(result))
        self.assertListAlmostEqual([0, 0], result[0:][6:][:2])
        self.assertListAlmostEqual([0, 1], result[8:][6:][:2])
        self.assertListAlmostEqual([1, 0], result[16:][6:][:2])
        self.assertListAlmostEqual([1, 1], result[24:][6:][:2])
        self.assertListAlmostEqual([2, 0], result[32:][6:][:2])
        self.assertListAlmostEqual([2, 1], result[40:][6:][:2])
        self.assertListAlmostEqual([3, 0], result[48:][6:][:2])
        self.assertListAlmostEqual([3, 1], result[56:][6:][:2])

    def test_convert_skips_negitive_value_verticies(self):
        test_array = np.array([[9, 8], [0, 6], [5, 4], [3, 2]])
        result = GLConverter().convert(test_array)
        self.assertEqual(8 * 7, len(result))

    def test_convert_is_fast(self):
        test_array = np.random.rand(720,10000)
        start = time.time()
        result = GLConverter().convert(test_array)
        total = time.time() - start
        self.assertTrue(total < 2.0)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()