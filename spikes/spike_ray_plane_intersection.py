import numpy as np

#  i_ -> Component
#  p_ -> Point
#  v_ -> Vector
#  n_ -> n_planeormal


class SpikeRayPlaneIntersection(object):
    def __init__(self, camera_focal_length_mm, mm_per_pixel, laser_intersection_degrees, center_intersection_point_xyz, camera_shape_xy):
        self.camera_focal_length_mm = camera_focal_length_mm
        self.mm_per_pixel = mm_per_pixel
        self.laser_intersection_degrees = laser_intersection_degrees
        self.center_intersection_point_xyz = center_intersection_point_xyz
        self.camera_shape_xy = camera_shape_xy

        self.n_laser_plane = self.laser_plane_normal(self.laser_intersection_degrees, self.center_intersection_point_xyz)
        self.intersection_array = self.get_intersection_array()

    def laser_plane_normal(self, laser_intersection_degrees, laser_intersection_point):
        i_x, i_y, i_z = laser_intersection_point
        p_1 = np.array([i_x, i_y, i_z])
        p_2 = np.array([i_x, i_y + 1.0, i_z])
        p_3 = np.array([-(np.tan(laser_intersection_degrees) * (i_z / -2.0)), 0, i_z / 2.0])

        v_21 = p_2 - p_1
        v_31 = p_3 - p_1

        return np.cross(v_21, v_31)

    def get_intersection_array(self):
        final = np.zeros((self.camera_shape_xy[0], self.camera_shape_xy[1], 3), dtype='float16')
        p_1 = np.array(self.center_intersection_point_xyz)
        n_plane = self.n_laser_plane
        with np.errstate(divide='ignore', invalid='ignore'):
            for x_camera in range(self.camera_shape_xy[0]):
                for y_camera in range(self.camera_shape_xy[1]):
                    x_pos = (x_camera - (self.camera_shape_xy[0] / 2)) * float(self.mm_per_pixel)
                    y_pos = (y_camera - (self.camera_shape_xy[1] / 2)) * float(self.mm_per_pixel)
                    z_pos = -self.camera_focal_length_mm

                    L2 = np.array([x_pos, y_pos, z_pos])
                    final[x_camera, y_camera] = (np.dot(n_plane, p_1) / np.dot(n_plane, L2)) * L2


        final[final == np.inf] = 0
        final[final == -np.inf] = 0
        final = np.nan_to_num(final)
        return final

    def get_points(self, frame):
        return self.intersection_array[frame]



# -----------------------TESTS------------------------------------------

import unittest
import time

class TestRayPlaneIntersections(unittest.TestCase):

    def test_center_pixel_is_center(self):
        srpi = SpikeRayPlaneIntersection(
                    camera_focal_length_mm=9,
                    mm_per_pixel=3,
                    laser_intersection_degrees=np.pi / 4.0,
                    center_intersection_point_xyz=[0, 0, -9],
                    camera_shape_xy=[3, 3]
                    )
        test_image = np.zeros((3, 3), dtype='bool')
        test_image[1, 1] = 1
        expected = np.array([[0, 0, -9]], dtype='float16')

        result = srpi.get_points(test_image)
        self.assertTrue((expected == result).all())

    def test_offset_pixel_is_correct(self):
        srpi = SpikeRayPlaneIntersection(
                    camera_focal_length_mm=9,
                    mm_per_pixel=4.5,
                    laser_intersection_degrees=np.pi / 4.0,
                    center_intersection_point_xyz=[0, 0, -9],
                    camera_shape_xy=[3, 3]
                    )
        test_image = np.ones((3, 3), dtype='bool')
        expected = np.array([
            [-3.0, -3.0,  -6.0],  # -1, -1
            [-3.0,  0.0,  -6.0],  # -1,  0 
            [-3.0,  3.0,  -6.0],  # -1,  1 
            [ 0,   -4.5,  -9.0],  #  0, -1
            [ 0,    0.0,  -9.0],  #  0,  0 
            [ 0,    4.5,  -9.0],  #  0,  1 
            [ 9.0, -9.0, -18.0],  #  1, -1
            [ 9.0,    0, -18.0],  #  1,  0 
            [ 9.0,  9.0, -18.0],  #  1,  1 
            ], dtype='float16')

        result = srpi.get_points(test_image)
        for idx in range(9):
            print "TEST:{}:  {} == {}".format(idx, expected[idx], result[idx])
            self.assertTrue(np.allclose(expected[idx], result[idx]))

    def test_camera_data_generation_correct(self):
        camera_shape = [1920, 1080]
        start = time.time()
        srpi = SpikeRayPlaneIntersection(
                    camera_focal_length_mm=0.1,
                    mm_per_pixel=0.004,
                    laser_intersection_degrees=np.pi / 4.0,
                    center_intersection_point_xyz=[0, 0, -150],
                    camera_shape_xy=camera_shape
                    )
        total = time.time() - start
        print ("Total: {}".format(total))
        print ("ms per point: {}".format((total / (camera_shape[0] * camera_shape[1]))*1000))


if __name__ == '__main__':
    unittest.main()