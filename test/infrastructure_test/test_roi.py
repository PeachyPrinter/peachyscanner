import unittest
import sys
import os
import numpy as np
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.roi import ROI


class ROITest(unittest.TestCase):
    def tarray(self):
        sample_array = np.ones((256, 256, 3), dtype='uint8')
        for y in range(256):
            for x in range(256):
                sample_array[x, y] = [x, y, 0]
        return sample_array

    def test_get_returns_roi_of_expected_size(self):
        test_array = self.tarray()
        roi = ROI(0, 0, test_array.shape[0], test_array.shape[1])
        self.assertTrue((roi.get(test_array) == test_array).all())

    def test_get_returns_roi_of_expected_details(self):
        test_array = self.tarray()
        roi = ROI(0, 0, 2, 2)
        result = roi.get(test_array)
        self.assertTrue((result[0][0] == [0, 0, 0,]).all())
        self.assertTrue((result[1][1] == [1, 1, 0,]).all())

    def test_get_returns_roi_of_expected_size_if_anything_unset(self):
        test_array = self.tarray()
        roi = ROI(0, 0,  None, None)
        self.assertTrue((roi.get(test_array) == test_array).all())

    def test_from_points_gets_roi_from_two_cordanates(self):
        test_array = self.tarray()
        roi = ROI(0, 0, None, None)
        p1 = (10, 20)
        p2 = (20, 10)
        roi.set_from_points(p1, p2)

        self.assertEquals(10, roi.get(test_array).shape[0])
        self.assertEquals(10, roi.get(test_array).shape[1])
        self.assertTrue((roi.get(test_array)[0][0] == [10, 10, 0]).all())

    def test_overlay_dims_surrounding_area(self):
        test_array = self.tarray()
        roi = ROI(0, 0, 128, 128)
        overlay = roi.overlay(test_array)
        self.assertTrue((overlay[254][254] == [127, 127, 0]).all(), "{}".format(overlay[255][255]))

    def test_replace_returns_only_new_part_if_no_data(self):
        test_array = self.tarray()
        newpart = np.ones(test_array.shape, dtype='uint8')
        roi = ROI()
        replaced = roi.replace(test_array, newpart)
        self.assertTrue((replaced == newpart).all())

    def test_copy_creates_copy(self):
        roi = ROI(45, 48, 12, 12)
        roi2 = roi.copy()
        self.assertEqual(roi.x, roi2.x)
        self.assertEqual(roi.y, roi2.y)
        self.assertEqual(roi.w, roi2.w)
        self.assertEqual(roi.h, roi2.h)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
