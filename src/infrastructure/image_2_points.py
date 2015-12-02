import numpy as np

class Image2Points(object):
    def __init__(
        self,
        hardware,
        camera_pixels_shape_yx,
    ):
        self._mm_per_pixel_yx = self._calculate_mm_per_pixel_yx(camera_pixels_shape_yx, hardware.sensor_size_xy_mm)
        self._laser_plane_normal_xyz = self._get_laser_plane_normal_xyz(hardware.center_intersection_xyz, hardware.laser_center_intersection_rad)
        self._posisition_mask_yx = self._get_laser_intersections_mask_yx(camera_pixels_shape_yx, hardware.focal_length_mm, self._mm_per_pixel_yx, hardware.center_intersection_xyz, hardware.center_intersection_xyz, self._laser_plane_normal_xyz)
        # self._posisition_mask_yx = self.one_to_one(camera_pixels_shape_yx)

    # def one_to_one(self, size):
    #     print "$" * 50
    #     print size
    #     a = np.ones((size[1], size[0], 3))
    #     for x in range(size[1]):
    #         for y in range(size[0]):
    #             f_x = ((float(x) / size[1]) * 2.0) - 1.0
    #             f_y = ((float(size[0]-y) / size[0]) * 2.0) - 1.0
    #             a[x, y] = [f_x, f_y, f_x]
    #     return a


    def _get_laser_intersections_mask_yx(
        self,
        camera_pixels_shape_yx,
        camera_focal_length_mm,
        mm_per_pixel_yx,
        center_intersection_xyz,
        laser_intersection_point,
        laser_plane_normal):

        final = np.zeros((camera_pixels_shape_yx[0], camera_pixels_shape_yx[1], 3), dtype='float16')
        laser_intersection_point = np.array(laser_intersection_point)
        with np.errstate(divide='ignore', invalid='ignore'):
            p_dot = np.dot(laser_plane_normal, laser_intersection_point)
            for y_camera in range(camera_pixels_shape_yx[0]):
                for x_camera in range(camera_pixels_shape_yx[1]):
                    x_pos = (x_camera - (camera_pixels_shape_yx[1] / 2)) * mm_per_pixel_yx[1]
                    y_pos = (y_camera - (camera_pixels_shape_yx[0] / 2)) * mm_per_pixel_yx[0]
                    z_pos = -camera_focal_length_mm

                    L2 = np.array([x_pos, y_pos, z_pos])
                    final[y_camera, x_camera] = (p_dot / np.dot(laser_plane_normal, L2)) * L2
        return final - center_intersection_xyz

    def _calculate_mm_per_pixel_yx(self, camera_pixels_shape_yx, camera_sensor_size_mm):
        x_mm_per_pixel = camera_sensor_size_mm[0] / float(camera_pixels_shape_yx[1])
        y_mm_per_pixel = camera_sensor_size_mm[1] / float(camera_pixels_shape_yx[0])
        return (y_mm_per_pixel, x_mm_per_pixel)

    def _get_laser_plane_normal_xyz(self, laser_intersection_point, laser_center_intersection_rad):
        i_x, i_y, i_z = laser_intersection_point
        p_1 = np.array([i_x, i_y, i_z])
        p_2 = np.array([i_x, i_y + 1.0, i_z])
        p_3 = np.array([-(np.tan(laser_center_intersection_rad) * (i_z / -2.0)), 0, i_z / 2.0])
        v_21 = p_2 - p_1
        v_31 = p_3 - p_1
        return np.cross(v_21, v_31)

    def _rotation_matrix(self, theta):
        rotation_axis = np.asarray([0, 1, 0], dtype='float16')
        theta = np.asarray(theta, dtype='float16')
        axis = rotation_axis/np.sqrt(np.dot(rotation_axis, rotation_axis))
        a = np.cos(theta / 2)
        b, c, d = -axis*np.sin(theta/2)
        a2, b2, c2, d2 = a*a, b*b, c*c, d*d
        bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
        return np.array([[a2+b2-c2-d2, 2*(bc+ad), 2*(bd-ac)],
                         [2*(bc-ad), a2+c2-b2-d2, 2*(cd+ab)],
                         [2*(bd+ac), 2*(cd-ab), a2+d2-b2-c2]])

    def _rotate_points(self, points_xyz, rotation_rad):
        rotation_matrix = self._rotation_matrix(rotation_rad)
        return np.dot(rotation_matrix, points_xyz.T).T

    def get_points(self, image_yx, rotation_rad, roi):
        roi_pos = roi.get(self._posisition_mask_yx)
        roi_image_yx = roi.get(image_yx).astype('bool')
        masked_result = roi_pos[roi_image_yx]
        return self._rotate_points(masked_result, rotation_rad)

    # def triangle(self):
    #     if hasattr(self, '_triangle'):
    #         return self._triangle
    #     dots = 50
    #     bottom = np.ones((dots, 3))
    #     bottom[:, 0] = np.linspace(-1, 1, dots)
    #     bottom[:, 1] = -1
    #     bottom[:, 2] = 0

    #     left = np.ones((dots, 3))
    #     left[:, 0] = np.linspace(-1, 0, dots)
    #     left[:, 1] = np.linspace(-1, 1, dots)
    #     left[:, 2] = 0

    #     right = np.ones((dots, 3))
    #     right[:, 0] = np.linspace(1, 0, dots)
    #     right[:, 1] = np.linspace(-1, 1, dots)
    #     right[:, 2] = 0

    #     self._triangle = np.vstack((bottom, left, right))
    #     return self._triangle

    # def cube(self):
    #     if hasattr(self, '_cube'):
    #         return self._cube
    #     dots = 50
    #     x = np.linspace(-1, 1, dots)
    #     edge = np.ones((dots, 3))

    #     edge1 = edge.copy()
    #     edge1[:, 0] = x

    #     edge2 = edge.copy()
    #     edge2[:, 1] = x

    #     edge3 = edge.copy()
    #     edge3[:, 2] = x

    #     edge4 = edge.copy()
    #     edge4[:, 1] = x
    #     edge4[:, 0] = -1

    #     edge5 = edge.copy()
    #     edge5[:, 2] = x
    #     edge5[:, 0] = -1

    #     edge7 = edge.copy()
    #     edge7[:, 0] = x
    #     edge7[:, 1] = -1

    #     edge9 = edge.copy()
    #     edge9[:, 2] = x
    #     edge9[:, 1] = -1

    #     edgeA = edge.copy()
    #     edgeA[:, 0] = x
    #     edgeA[:, 2] = -1

    #     edgeB = edge.copy()
    #     edgeB[:, 1] = x
    #     edgeB[:, 2] = -1

    #     edge6 = edge.copy()
    #     edge6[:, 0] = x
    #     edge6[:, 1] = -1
    #     edge6[:, 2] = -1

    #     edge8 = edge.copy()
    #     edge8[:, 1] = x
    #     edge8[:, 0] = -1
    #     edge8[:, 2] = -1

    #     edgeC = edge.copy()
    #     edgeC[:, 2] = x
    #     edgeC[:, 0] = -1
    #     edgeC[:, 1] = -1

    #     self._cube = np.vstack((edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9, edgeA, edgeB, edgeC))
    #     return self._cube