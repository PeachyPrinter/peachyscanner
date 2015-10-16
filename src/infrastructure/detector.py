import cv2
import numpy as np


class Detector(object):
    def __init__(self, roi, point_converter):
        self.OVERLAY_COLOR = np.array((0, 255, 0), dtype='uint8')
        self.lo_range_bgr = (64, 64, 64)
        self.hi_range_bgr = (172, 172, 172)
        self._roi = roi
        self._point_converter = point_converter
        self._last_points = None
        self._mask = None

    def process(self, frame):
        self._mask = cv2.inRange(frame, self.lo_range_bgr, self.hi_range_bgr)

    def overlay_mask(self, frame):
        region = self._roi.get(frame)
        mask = self._roi.get(self._mask)
        green = np.ones(region.shape, dtype='uint8') * self.OVERLAY_COLOR
        mask_inv = cv2.bitwise_not(mask)
        black = cv2.bitwise_and(region, region, mask=mask_inv)
        green = cv2.bitwise_and(green, green, mask=mask)
        overlay = cv2.add(black, green)
        return self._roi.replace(frame, overlay)

    def replace_mask(self, frame):
        pass

    def points(self):
        pass
