class ROI(object):
    def __init__(self, x=None, y=None, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set(self,x,y,w,h):
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
        gray = frame * amount
        roi = self.get(frame)
        gray[self.y:self.y + self.w, self.x:self.x + self.h] = roi
        return gray

    def get(self, frame):
        if self.x is not None and self.y is not None and self.w is not None and self.h is not None:
            return frame[self.y:self.y + self.w, self.x:self.x + self.h]
        else:
            return frame