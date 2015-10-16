import cv2
import numpy as np


class Detector(object):
    def __init__(self, point_converter):
        self.OVERLAY_COLOR = np.array((0, 255, 0), dtype='uint8')
        self.lo_range_bgr = (64, 64, 64)
        self.hi_range_bgr = (172, 172, 172)
        self._point_converter = point_converter
        self._last_points = None
        self._mask = None

    def process(self, frame, roi):
        self._roi = roi.copy()
        region = self._roi.get(frame)
        self._mask = cv2.inRange(region, self.lo_range_bgr, self.hi_range_bgr)

    def overlay_mask(self, frame):
        region = self._roi.get(frame)
        green = np.ones(region.shape, dtype='uint8') * self.OVERLAY_COLOR
        mask_inv = cv2.bitwise_not(self._mask)
        black = cv2.bitwise_and(region, region, mask=mask_inv)
        green = cv2.bitwise_and(green, green, mask=self._mask)
        overlay = cv2.add(black, green)
        return self._roi.replace(frame, overlay)

    def replace_mask(self, frame):
        pass

    def points(self, frame):
        mask_center = (frame.shape[1] / 2) - self._roi.x
        return self._point_converter.get_points(self._mask, mask_center)
