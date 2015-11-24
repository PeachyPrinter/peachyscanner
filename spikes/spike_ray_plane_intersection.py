import numpy as np

#  i_ -> Component
#  p_ -> Point
#  v_ -> Vector
#


class SpikeRayPlaneIntersection(object):
    def __init__(self,
        camera_focal_length_mm,
        pixels_per_mm,
        laser_intersection_degrees,
        center_intersection_point_xyz,
        camera_shape_xy
        ):
        self.camera_focal_length_mm = camera_focal_length_mm
        self.pixels_per_mm = pixels_per_mm
        self.laser_intersection_degrees = laser_intersection_degrees
        self.center_intersection_point_xyz = center_intersection_point_xyz
        self.camera_shape_xy = camera_shape_xy

        self.n_laser_plane = self.get_laser_plane_equation(self.laser_intersection_degrees, self.center_intersection_point_xyz)
        print ("Plane Normal: \n%s" % self.n_laser_plane)
        self.intersection_array = self.get_intersection_array()


    def get_laser_plane_equation(self, laser_intersection_degrees, laser_intersection_point):
        i_x, i_y, i_z = laser_intersection_point
        P1 = np.array([i_x, i_y, i_z])
        P2 = np.array([i_x, i_y + 1.0, i_z])
        P3 = np.array([-(np.tan(laser_intersection_degrees) * (i_z / -2.0)), 0, i_z / 2.0])

        v_PQ = P2 - P1
        v_PR = P3 - P1

        return np.cross(v_PQ, v_PR).reshape(1, 3)

    def get_intersection_array(self):
        final = np.zeros((self.camera_shape_xy[0], self.camera_shape_xy[1], 3))
        for x_camera in range(self.camera_shape_xy[0]):
            for y_camera in range(self.camera_shape_xy[1]):
                x_pos = x_camera - (self.camera_shape_xy[0] / 2)
                y_pos = y_camera - (self.camera_shape_xy[1] / 2)
                z_pos = -self.camera_focal_length_mm

                P1 = np.array(self.center_intersection_point_xyz)
                L2 = np.array([x_pos, y_pos, z_pos])
                L1 = np.array([0, 0, 0])
                N = self.n_laser_plane

                with np.errstate(divide='ignore', invalid='ignore'):
                    result = L1 + np.dot(N, P1 - L1) / np.dot(N, L2 - L1) * (L2 - L1)
                    result[result == np.inf] = 0
                    result[result == -np.inf] = 0
                    result = np.nan_to_num(result)
                final[x_camera, y_camera] = result
        print "Final: \n%s" % final
        return final


    def get_points(self, frame):
        return self.intersection_array[frame]



# -------------------------------------------------------------

import unittest

class TestRayPlaneIntersections(unittest.TestCase):

    # def test_center_pixel_is_center(self):
    #     srpi = SpikeRayPlaneIntersection(
    #                 camera_focal_length_mm = 1,
    #                 pixels_per_mm = 1,
    #                 laser_intersection_degrees = np.pi / 4.0,
    #                 center_intersection_point_xyz = [0, 1, 0],
    #                 camera_shape_xy = [3, 3]
    #                 )
    #     test_image = np.zeros((3, 3), dtype='bool')
    #     test_image[1,1] = 1
    #     expected = np.array([[0, 0, 0]])

    #     result = srpi.get_points(test_image)
    #     print result
    #     self.assertTrue((expected == result).all())

    def test_offset_pixel_is_correct(self):
        srpi = SpikeRayPlaneIntersection(
                    camera_focal_length_mm = 1,
                    pixels_per_mm = 1,
                    laser_intersection_degrees = np.pi / 4.0,
                    center_intersection_point_xyz = [0, 0, -1],
                    camera_shape_xy = [3, 3]
                    )
        test_image = np.ones((3, 3), dtype='bool')
        expected = np.array([
        [ -0.5, -0.5,  -0.5],  # -1,  -1
        [ -0.5,    0,  -0.5],  # -1,  0 
        [ -0.5,  0.5,  -0.5],  # -1,  1 
        [  0,   -0.5,  -0.5],  #  0, -1
        [  0,      0,   0  ],  #  0,  0 
        [  0,    0.5,  -0.5],  #  0,  1 
        [  0.5,  -0.5, -0.5],  #  1, -1
        [  0.5,     0, -0.5],  #  1,  0 
        [  0.5,   0.5, -0.5],  #  1,  1 
        ])

        result = srpi.get_points(test_image)
        print "TEST::  %s" % "\n%%%%\n"

        for idx in range(9):
            print "TEST:{}:  {} == {}".format(idx, expected[idx], result[idx])
            self.assertTrue(np.allclose(expected[idx], result[idx]))



if __name__ == '__main__':
    unittest.main()