import numpy as np
import logging

logger = logging.getLogger('peachy')


class Handler(object):

    def __init__(self, sections):
        self.sections = sections
        self._section_count = 0

    def handle():
        raise NotImplementedError()

    @property
    def complete(self):
        return self._section_count >= self.sections

    @property
    def status(self):
        return self._section_count / float(self.sections)


class ImageCapture(Handler):
    def __init__(self, sections, section_offset=0):
        super(ImageCapture, self).__init__(sections)
        self.section_offset = section_offset
        self.image = None

    def handle(self, frame=None, section=0, **kwargs):
        self._section_count += 1
        current_section  = (section + self.section_offset) % self.sections
        self._image(frame.shape[0])[:, current_section] = frame[:, -1]
        return self._section_count < self.sections

    def _image(self, y_axis_dimension):
        if self.image is None:
            self.image = np.zeros((y_axis_dimension, self.sections, 3), dtype='uint8')
        return self.image


class PointCaptureXYZ(Handler):
    def __init__(self, sections, img2points, laser_theta, points_xyz=None, ):
        super(PointCaptureXYZ, self).__init__(sections)
        self.img2points = img2points
        self.laser_theta = laser_theta
        self.sections = sections
        self._section_count = 0
        self.points_xyz = points_xyz

    def handle(self, laser_detection=None, section=0, roi=None, **kwargs):
        rad = (section / float(self.sections)) * 2.0 * np.pi
        points = self.img2points.get_points(laser_detection, rad, roi, self.laser_theta)
        if self.points_xyz is None:
            self.points_xyz = points
        else:
            self.points_xyz = np.vstack((self.points_xyz, points))
        self._section_count += 1
        return self._section_count < self.sections
