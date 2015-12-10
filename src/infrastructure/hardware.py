import numpy as np

class HardwareConfiguration(object):
    def __init__(
        self,
        focal_length_mm,
        sensor_size_xy_mm,
        focal_point_to_center_mm,
        intersections_rad_mm
        ):
        assert(len(sensor_size_xy_mm) == 2)
        self.focal_length_mm = focal_length_mm
        self.sensor_size_xy_mm = sensor_size_xy_mm
        self.focal_point_to_center_mm = focal_point_to_center_mm
        self.intersections_rad_mm = intersections_rad_mm

    @property
    def center_intersection_xyz(self):
        return np.array([0, 0, -self.focal_point_to_center_mm])

    @property
    def laser_intersections_rad_xyz(self):
        return [(rad, np.array([0, 0, -pos])) for (rad, pos) in self.intersections_rad_mm]
