import logging

logger = logging.getLogger('peachy')


class ROI(object):
    def __init__(self, x, y, w, h, frame_shape):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.frame_shape = frame_shape
        self.center_line = frame_shape[1] // 2
        if self.center_line > (self.x + self.w) or self.center_line < self.x:
            raise Exception('Region of interest must span the center of frame')

    @classmethod
    def set_from_points(cls, point1, point2, frame_shape):
        x = min(point1[0], point2[0])
        y = min(point1[1], point2[1])
        w = abs(point1[0] - point2[0])
        h = abs(point1[1] - point2[1])
        return ROI(x, y, w, h, frame_shape)

    def overlay(self, frame, amount=0.5):
        gray = frame / int(1 / amount)
        roi = self.get(frame)
        return self.replace(gray, roi)

    def replace(self, full_frame, new_part):
        if self._complete():
            full_frame[self.y:self.y + self.h, self.x:self.x + self.w] = new_part
            return full_frame
        else:
            return new_part

    def get(self, frame):
        if self._complete():
            return frame[self.y:self.y + self.h, self.x:self.x + self.w]
        else:
            return frame

    def copy(self):
        return ROI(self.x, self.y, self.w, self.h, self.frame_shape)

    def get_left_of_center(self, frame):
        return frame[self.y:self.y + self.h, self.x:self.center_line]

    def _complete(self):
        return not (self.x is None or self.y is None or self.w is None or self.h is None)
