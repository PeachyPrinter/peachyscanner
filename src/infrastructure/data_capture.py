import numpy as np

# from infrastructure.point_converter import PointConverter

class ImageCapture(object):

    def __init__(self, sections):
        self.sections = sections
        self._section_count = 0
        self.image = None

    def handle(self, frame=None, section=0):
        self._section_count += 1
        self._image(frame.shape[0])[:, section] = frame[:, -1]
        return self._section_count < self.sections

    def _image(self, y_axis_dimension):
        if self.image is None:
            self.image = np.zeros((y_axis_dimension, self.sections, 3), dtype='uint8')
        return self.image


class PointCapture(object):

    def __init__(self, sections):
        self.sections = sections
        self._section_count = 0
        self.point_converter = PointConverter()
        self.points = None

    def handle(self, **kwargs):
        self._section_count += 1
        points = self._points(kwargs['detected'].shape[0])
        data = kwargs['detected'].copy()
        section = kwargs['section']
        points[:, section] = self.point_converter.get_points(data, kwargs['roi_center_y'])
        return self._section_count < self.sections

    def _points(self, height):
        if self.points is None:
            self.points = np.zeros((height, self.sections), dtype='int32')
        return self.points


class PointConverter(object):
    def get_points(self, mask, center):
        roi = mask
        maxindex = np.argmax(roi, axis=1)
        data = (np.ones(maxindex.shape[0]) * center) - maxindex
        data[data < 0] = 0
        data[data == center] = 0
        return data
