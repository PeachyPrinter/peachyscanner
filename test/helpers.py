import unittest
import cv2
import os


class TestHelpers(unittest.TestCase):
    def assertListAlmostEqual(self, list1, list2, decimals=None, msg=None):
        if not msg:
            new_msg = '{} did not almost equal {}'.format(list1, list2)
        else:
            new_msg = msg
        self.assertEqual(len(list1), len(list2), new_msg)
        for idx in range(0, len(list1)):
            if not msg:
                new_msg = '{} did not almost equal {} as {} was not {}'.format(list1, list2, list1[idx], list2[idx])
            else:
                new_msg = msg
            self.assertAlmostEqual(list1[idx], list2[idx], decimals, new_msg)

    def assertROIEquals(self, roi1, roi2):
        self.assertEqual(roi1.x, roi2.x)
        self.assertEqual(roi1.y, roi2.y)
        self.assertEqual(roi1.w, roi2.w)
        self.assertEqual(roi1.h, roi2.h)
        self.assertEqual(roi1.frame_shape, roi2.frame_shape)


class FakeCamera(object):
    def __init__(self, image=None, file_image='fake_image.png'):
        if image is not None:
            self.image = image
        else:
            path = os.path.dirname(__file__)
            image = cv2.imread(os.path.join(path, file_image))
            self.image = image
        self.calls = -1

    def read(self):
        self.calls += 1
        a = self.image[:, -1]
        b = self.image[:, 1:]
        self.image[:, 0] = a
        self.image[:, 1:] = b
        return self.image
