
class Detector(object):
    def __init__(self, roi, point_converter):
        self.lo_range_bgr = (0, 0, 0)
        self.hi_range_bgr = (255, 255, 255)
        self._roi = roi
        self._point_converter = point_converter

    def process(self, frame):
        pass

    def overlay_mask(self, frame, color):
        pass

    def replace_mask(self, frame, color):
        pass

    def points(self):
        pass
