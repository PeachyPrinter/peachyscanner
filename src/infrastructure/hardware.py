import numpy as np

class HardwareConfiguration(object):
    def __init__(
        self,
        focal_length_mm,
        sensor_size_xy_mm,
        focal_point_to_center_mm,
        laser_center_intersection_rad,
        ):
        assert(len(sensor_size_xy_mm) == 2)
        self.focal_length_mm = focal_length_mm
        self.sensor_size_xy_mm = sensor_size_xy_mm
        self.focal_point_to_center_mm = focal_point_to_center_mm
        self.laser_center_intersection_rad = laser_center_intersection_rad

    @property
    def center_intersection_xyz(self):
        return np.array([0, 0, -self.focal_point_to_center_mm])
