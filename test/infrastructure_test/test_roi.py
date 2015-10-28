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

    def test_get_points_should_return_a_list_of_points(self):
        roi = ROI(0, 0, 1, 1)
        self.assertEquals([0, 0, 1, 1], roi.get_points())

    def test_get_returns_roi_of_expected_size(self):
        test_array = self.tarray()
        roi = ROI(0, 0, 1, 1)
        self.assertTrue((roi.get(test_array) == test_array).all())

    def test_get_returns_roi_of_expected_details(self):
        test_array = self.tarray()
        roi = ROI.set_from_abs_points((127, 0), (129, 2), self.tarray().shape)
        result = roi.get(test_array)
        self.assertTrue((result[0][0] == [0, 127, 0]).all())
        self.assertTrue((result[1][1] == [1, 128, 0]).all())

    def test_from_points_gets_roi_from_two_cordanates(self):
        test_array = self.tarray()
        p1 = (10, 20)
        p2 = (200, 10)
        roi = ROI.set_from_abs_points(p1, p2, test_array.shape)

        self.assertEquals(10, roi.get(test_array).shape[0])
        self.assertEquals(190, roi.get(test_array).shape[1])
        self.assertTrue((roi.get(test_array)[0][0] == [10, 10, 0]).all())

    def test_overlay_dims_surrounding_area(self):
        test_array = self.tarray()
        roi = ROI.set_from_abs_points((0, 0), (128, 128), self.tarray().shape)
        overlay = roi.overlay(test_array)
        self.assertTrue((overlay[254][254] == [127, 127, 0]).all(), "{}".format(overlay[255][255]))

    def test_replace_returns_only_new_part_if_no_data(self):
        test_array = self.tarray()
        newpart = np.ones(test_array.shape, dtype='uint8')
        roi = ROI.set_from_abs_points((0, 0), (256, 256), self.tarray().shape)
        replaced = roi.replace(test_array, newpart)
        self.assertTrue((replaced == newpart).all())

    def test_copy_creates_copy(self):
        roi = ROI.set_from_abs_points((45, 48), (173, 12), self.tarray().shape)
        roi2 = roi.copy()
        self.assertEqual(roi.x_rel, roi2.x_rel)
        self.assertEqual(roi.y_rel, roi2.y_rel)
        self.assertEqual(roi.w_rel, roi2.w_rel)
        self.assertEqual(roi.h_rel, roi2.h_rel)

    def test_get_left_of_center_returns_portion_of_frame_in_roi_left_of_the_center_line(self):
        expected = np.ones((25, 65, 3), dtype='uint8')
        frame = np.ones((100, 150, 3), dtype='uint8')
        roi = ROI.set_from_abs_points((10, 10), (80, 35), frame.shape)
        clipped_frame = roi.get_left_of_center(frame)
        self.assertEquals(expected.shape, clipped_frame.shape)
        self.assertTrue((expected == clipped_frame).all())

    def test_should_raise_exception_if_center_is_not_in_roi(self):
        frame = np.ones((100, 100, 3), dtype='uint8')
        with self.assertRaises(Exception):
            ROI.set_from_abs_points((10, 10), (20, 20), frame.shape)

    def test_should_raise_exception_if_center_left_of_roi(self):
        frame = np.ones((100, 100, 3), dtype='uint8')
        with self.assertRaises(Exception):
            ROI.set_from_abs_points((70, 10), (80, 20), frame.shape)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
