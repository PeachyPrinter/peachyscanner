import logging

logger = logging.getLogger('peachy')

class ROI(object):
    def __init__(self, x=0, y=0, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set_from_points(self, point1, point2):
        self.x = min(point1[0], point2[0])
        self.y = min(point1[1], point2[1])
        self.w = abs(point1[0] - point2[0])
        self.h = abs(point1[1] - point2[1])

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

    def _complete(self):
        return not (self.x is None or self.y is None or self.w is None or self.h is None)