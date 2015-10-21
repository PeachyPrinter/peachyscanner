import unittest
import cv2
import os
import numpy as np

class TestHelpers(unittest.TestCase):
    def assertListAlmostEqual(self, list1, list2, decimals=None, msg=None):
        if not msg:
            new_msg = '{} did not almost equal {}'.format(list1,list2)
        else:
            new_msg = msg
        self.assertEqual(len(list1), len(list2), new_msg)
        for idx in range(0, len(list1)):
            if not msg:
                new_msg = '{} did not almost equal {} as {} was not {}'.format(list1, list2, list1[idx], list2[idx])
            else:
                new_msg = msg
            self.assertAlmostEqual(list1[idx], list2[idx], decimals, new_msg)

class FakeCamera(object):

    def __init__(self, image=None, file_image='fake_image.png'):
        if image is not None:
            self.image = image
        else:
            path = os.path.dirname(__file__)
            print (os.path.join(path, file_image))
            image = cv2.imread(os.path.join(path, file_image))
            self.image = image
        self.calls = -1

    def read(self):
        self.calls += 1
        idx = self.calls % self.image.shape[0]
        return self.image
        # return cv2.warpAffine(self.image, np.array([[1,0,idx], [0,1,0]]), tuple(self.image.shape[:2]))