import numpy as np
import logging

logger = logging.getLogger('peachy')

class Image2Points(object):
    def __init__(
        self,
        hardware,
        camera_pixels_shape_yx,
    ):
        self._mm_per_pixel_yx = self._calculate_mm_per_pixel_yx(camera_pixels_shape_yx, hardware.sensor_size_xy_mm)
        self._posisition_mask_yx = {}
        self.laser_plane_normals = {}
        for (theta, pos) in hardware.laser_intersections_rad_xyz:
            self.laser_plane_normals[theta] = self._get_laser_plane_normal_xyz(pos, theta)
            self._posisition_mask_yx[theta] = self._get_laser_intersections_mask_yx(
                camera_pixels_shape_yx,
                hardware.focal_length_mm,
                self._mm_per_pixel_yx,
                hardware.center_intersection_xyz,
                pos,
                self.laser_plane_normals[theta])

    def get_data(self, 
        camera_pixels_shape_yx,
        camera_focal_length_mm,
        mm_per_pixel_yx,
        center_intersection_xyz,
        laser_intersection_point,
        laser_plane_normal,
        half_camera_yx,
        half_pixel_yx):

        return ("camera_pixels_shape_yx:    {: 4.3f}, {: 4.3f}\n".format(*camera_pixels_shape_yx) +
        "half_camera_yx:            {: 4.3f}, {: 4.3f}\n".format(*half_camera_yx) +
        "half_pixel_yx:             {: 4.3f}, {: 4.3f}\n".format(*half_pixel_yx) +
        "camera_focal_length_mm:    {: 4.3f}\n".format(camera_focal_length_mm) +
        "mm_per_pixel_yx:           {: 4.3f}, {: 4.3f}\n".format(*mm_per_pixel_yx) +
        "center_intersection_xyz:   {: 4.3f}, {: 4.3f}, {: 4.3f}\n".format(*center_intersection_xyz) +
        "laser_intersection_point:  {: 4.3f}, {: 4.3f}, {: 4.3f}\n".format(*laser_intersection_point) +
        "laser_plane_normal:        {: 4.3f}, {: 4.3f}, {: 4.3f}\n".format(*laser_plane_normal))


    def _get_laser_intersections_mask_yx(
                            self,
                            camera_pixels_shape_yx,
                            camera_focal_length_mm,
                            mm_per_pixel_yx,
                            center_intersection_xyz,
                            laser_intersection_point,
                            laser_plane_normal
                        ):
        half_camera_yx = (camera_pixels_shape_yx[0] / 2.0, camera_pixels_shape_yx[1] / 2.0)
        half_pixel_yx = (mm_per_pixel_yx[0] / 2.0, mm_per_pixel_yx[1] / 2.0)

        logger.debug(self.get_data( camera_pixels_shape_yx, camera_focal_length_mm, mm_per_pixel_yx, center_intersection_xyz, laser_intersection_point, laser_plane_normal, half_camera_yx, half_pixel_yx))

        final = np.zeros((camera_pixels_shape_yx[0], camera_pixels_shape_yx[1], 3), dtype='float16')
        laser_intersection_point = np.array(laser_intersection_point)
        with np.errstate(divide='ignore', invalid='ignore'):
            p_dot = np.dot(laser_plane_normal, laser_intersection_point)
            for x_camera in range(camera_pixels_shape_yx[1]):
                for y_camera in range(camera_pixels_shape_yx[0]):
                    x_pos = ((x_camera - half_camera_yx[1]) * mm_per_pixel_yx[1]) + half_pixel_yx[1]
                    y_pos = (((camera_pixels_shape_yx[0] - y_camera) - half_camera_yx[0]) * mm_per_pixel_yx[0]) - half_pixel_yx[0]
                    z_pos = -camera_focal_length_mm

                    L2 = np.array([x_pos, y_pos, z_pos])
                    final[y_camera, x_camera] = (p_dot / np.dot(laser_plane_normal, L2)) * L2
                    x, y, z = final[y_camera, x_camera]
                    logger.debug("({}, {}) => ({: .3f}, {: .3f}, {: .3f}) => {: .3f},{: .3f},{: .3f}".format(x_camera, y_camera, x_pos, y_pos, z_pos, x, y, z))
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
        vec = np.cross(v_21, v_31)
        unit_vec = vec / np.linalg.norm(vec)
        return unit_vec

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

    def get_points(self, image_yx, rotation_rad, roi, laser_theta):
        roi_pos = roi.get(self._posisition_mask_yx[laser_theta])
        roi_image_yx = roi.get(image_yx).astype('bool')
        masked_result = roi_pos[roi_image_yx]
        return self._rotate_points(masked_result, rotation_rad)