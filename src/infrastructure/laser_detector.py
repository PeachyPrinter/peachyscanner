import cv2
import numpy as np
from scipy import ndimage


class LaserDetector(object):
    def __init__(self, low_bgr, high_bgr):
        for idx in range(3):
            if low_bgr[idx] > high_bgr[idx]:
                raise Exception('Low range exceeds high range {} !< {}'.format(str(low_bgr), str(high_bgr)))
        self.low_bgr = low_bgr
        self.high_bgr = high_bgr

    @classmethod
    def from_rgb_float(cls, low_rgb, high_rgb):
        low = (int(low_rgb[2] * 255), int(low_rgb[1] * 255), int(low_rgb[0] * 255))
        high = (int(high_rgb[2] * 255), int(high_rgb[1] * 255), int(high_rgb[0] * 255))
        return cls(low, high)

    def detect(self, frame):
        return cv2.inRange(frame, self.low_bgr, self.high_bgr)


class LaserDetector2(object):
    color_map = {'red': 2, 'green': 1, 'blue': 0}

    def __init__(self, threshold=225, filter_size_yx=(3, 3), color='red'):
        self.filter_size_yx = filter_size_yx
        self.color = color
        self.threshold = threshold
        self._structure = np.ones(filter_size_yx)

    @property
    def color(self):
        return [key for (key, value) in self.color_map.items() if value == self._color][0]

    @color.setter
    def color(self, value):
        if value in self.color_map:
            self._color = self.color_map[value]
        else:
            raise Exception("Colors must be one of: {} was {}".format(str(self.color_map.keys()), value))

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        if (value < 0 or value >= 256):
            raise Exception('Threshold value must be uint8 type')
        self._threshold = value

    @property
    def filter_size_yx(self):
        return self._structure.shape

    @filter_size_yx.setter
    def filter_size_yx(self, value):
        if len(value) != 2:
            raise Exception('Filter size is a tuple')
        if value[0] < 1 or value[1] < 1:
            raise Exception('Filter must be at least (1,1) was {}'.format(str(value)))
        self._structure = np.ones(value)

    def detect(self, frame):
        b, g, r = cv2.split(frame)
        ab, ag, ar = np.average(b), np.average(g), np.average(r)
        b = self.sub(b, ab)
        g = self.sub(g, ag)
        r = self.sub(r, ar)
        rel = self.sub(r, g)
        ranged_image = cv2.inRange(rel, self._threshold, 255)
        noise_reduction = ndimage.binary_erosion(ranged_image, structure=self._structure).astype(ranged_image.dtype) * 255
        return noise_reduction

    def sub(self, a, b):
        sub1 = a - b
        mask = a < b
        sub1[mask] = 0
        return sub1.astype('uint8')
