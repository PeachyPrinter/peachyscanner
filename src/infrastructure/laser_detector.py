import cv2


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
