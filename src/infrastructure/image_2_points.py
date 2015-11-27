import numpy as np

class Image2Points(object):
    def __init__(
        self,
        camera_focal_length_mm,
        camera_sensor_size_mm,
        camera_pixels_shape_xy,
        laser_center_intersection_rad,
        center_intersection_xyz,
    ):
        self._mm_per_pixel = self._mm_per_pixel(camera_pixels_shape_xy, camera_sensor_size_mm)
        self._laser_plane_normal = self._get_laser_plane_normal(center_intersection_xyz, laser_center_intersection_rad)
        self._posisition_mask = self._get_laser_intersections_mask(camera_pixels_shape_xy, camera_focal_length_mm, self._mm_per_pixel, center_intersection_xyz, self._laser_plane_normal)

    def _get_laser_intersections_mask(
        self,
        camera_pixels_shape_xy,
        camera_focal_length_mm,
        mm_per_pixel,
        laser_intersection_point,
        laser_plane_normal):

        final = np.zeros((camera_pixels_shape_xy[0], camera_pixels_shape_xy[1], 3), dtype='float16')
        laser_intersection_point = np.array(laser_intersection_point)
        with np.errstate(divide='ignore', invalid='ignore'):
            p_dot = np.dot(laser_plane_normal, laser_intersection_point)
            for x_camera in range(camera_pixels_shape_xy[0]):
                for y_camera in range(camera_pixels_shape_xy[1]):
                    x_pos = (x_camera - (camera_pixels_shape_xy[0] / 2)) * mm_per_pixel[0]
                    y_pos = (y_camera - (camera_pixels_shape_xy[1] / 2)) * mm_per_pixel[1]
                    z_pos = -camera_focal_length_mm

                    L2 = np.array([x_pos, y_pos, z_pos])
                    final[x_camera, y_camera] = (p_dot / np.dot(laser_plane_normal, L2)) * L2
        return final

    def _mm_per_pixel(self, camera_pixels_shape_xy, camera_sensor_size_mm):
        x_mm_per_pixel = camera_sensor_size_mm[0] / float(camera_pixels_shape_xy[0])
        y_mm_per_pixel = camera_sensor_size_mm[1] / float(camera_pixels_shape_xy[1])
        return (x_mm_per_pixel, y_mm_per_pixel)

    def _get_laser_plane_normal(self, laser_intersection_point, laser_center_intersection_rad):
        i_x, i_y, i_z = laser_intersection_point
        p_1 = np.array([i_x, i_y, i_z])
        p_2 = np.array([i_x, i_y + 1.0, i_z])
        p_3 = np.array([-(np.tan(laser_center_intersection_rad) * (i_z / -2.0)), 0, i_z / 2.0])
        v_21 = p_2 - p_1
        v_31 = p_3 - p_1
        return np.cross(v_21, v_31)

    def get_points(self, image, rotation_rad, roi):
        return self._posisition_mask[image]
