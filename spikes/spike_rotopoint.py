import numpy as np

class RotoPoint(object):
    def __init__(self):
        pass

    def rotation_matrix(self, theta):
        axis = np.asarray([0, 1, 0], dtype='float16')
        theta = np.asarray(theta, dtype='float16')
        axis = axis/np.sqrt(np.dot(axis, axis))
        a = np.cos(theta/2)
        b, c, d = -axis*np.sin(theta/2)
        aa, bb, cc, dd = a*a, b*b, c*c, d*d
        bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
        return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                         [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                         [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

    def rotate_points(self, points_xyz, angle):
        r_mat = self.rotation_matrix(angle)

        return np.dot(r_mat, points_xyz.T).T



# -----------------------TESTS------------------------------------------

import unittest
import time

class TestRotoPoint(unittest.TestCase):
    def setUp(self):
        self.rotopoint = RotoPoint()

    def test_rotate_points_rotates_one_point_abount_y_axis(self):
        points = np.array([[1, 1, 1]], dtype='float16')
        expected = np.array([[1, 1, -1]], dtype='float16')

        result = self.rotopoint.rotate_points(points, np.pi / 2.0)
        print(result)
        print(expected)
        self.assertTrue(np.allclose(expected, result, rtol=1e-03))

    def test_rotate_points_rotates_two_point_abount_y_axis(self):
        points = np.array([[1, 1, 1], [0, 0, 0]], dtype='float16')
        expected = np.array([[1, 1, -1], [0, 0, 0]], dtype='float16')

        result = self.rotopoint.rotate_points(points, np.pi / 2.0)
        print(result)
        print(expected)
        self.assertTrue(np.allclose(expected, result, rtol=1e-03))

    def test_rotate_points_rotates_points_abount_y_axis_fast(self):
        test_items = 1000
        points = np.random.random((test_items, 3)).astype('float16')

        start = time.time()
        result = self.rotopoint.rotate_points(points, np.pi / 2.0)
        total = time.time() - start

        print("Time: {}ms or {}/ms".format(total * 1000, test_items / (total *1000)))
        self.assertTrue(total * 1000 < 1.0, total)


if __name__ == '__main__':
    unittest.main()