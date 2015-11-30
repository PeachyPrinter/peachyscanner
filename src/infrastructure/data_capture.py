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


class PointCapture(Handler):
    def __init__(self, sections):
        super(PointCapture, self).__init__(sections)
        self.point_converter = PointConverter()
        self.points_tyr = None  #(theta, height, radius)

    def handle(self, partial_laser_detection=None, section=0, roi_center_y=0, **kwargs):
        self._section_count += 1
        points = self._points(partial_laser_detection.shape[0])
        points[section] = self.point_converter.get_points(partial_laser_detection, partial_laser_detection.shape[0])
        return self._section_count < self.sections

    def _points(self, height):
        if self.points_tyr is None:
            self.points_tyr = np.zeros((self.sections, height), dtype='int32')
        return self.points_tyr


class PointConverter(object):
    def get_points(self, mask, center_y):
        roi = np.fliplr(mask)
        maxindex = np.argmax(roi, axis=1)
        missing_index = np.where(maxindex == 0)[0]
        if len(missing_index) > 0:
            last_valid_index = max(missing_index[0] - 1, 0)
            for index in missing_index:
                if index + 1  >= maxindex.shape[0]:
                    break
                if maxindex[index + 1] != 0:
                    total = index - last_valid_index
                    start = maxindex[last_valid_index]
                    stop = maxindex[index + 1]
                    samples = np.linspace(start, stop, num=total + 1,endpoint=False)
                    samples = samples[1:]
                    maxindex[last_valid_index + 1 :index + 1] = samples
                    last_valid_index = index + 1
        return maxindex


class PointCaptureXYZ(Handler):
    def __init__(self, sections, img2points):
        super(PointCaptureXYZ, self).__init__(sections)
        self.img2points = img2points
        self.sections = sections
        self._section_count = 0
        self.points_xyz = None

    def handle(self, laser_detection=None, section=0, roi=None):
        rad = (section / float(self.sections)) * 2.0 * np.pi
        points = self.img2points.get_points(laser_detection, rad, roi)
        if self.points_xyz is None:
            self.points_xyz = points
        else:
            self.points_xyz = np.vstack((self.points_xyz, points))
        self._section_count += 1
        return self._section_count < self.sections
