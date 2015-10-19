import logging
import numpy as np
import cv2

logger = logging.getLogger('peachy')

class Encoder(object):
    def __init__(self,
                 point=(0, 0),
                 threshold=382,
                 null_zone=382,
                 history_length=20
                 ):
        self.threshold = threshold
        self.null_zone = null_zone
        self.point = tuple(point)
        self.ENCODER_COLOR_LOW_BGR =  (0,   0,   255)
        self.ENCODER_COLOR_HIGH_BGR = (0,   255, 0  )
        self.ENCODER_COLOR_NULL_BGR = (0,   255, 255)
        self.THRESHOLD_MARKER_COLOR = (255, 255, 255)

        self.history_length = history_length

        self._color_bgr = self.ENCODER_COLOR_LOW_BGR
        self._is_high = False
        self._history = []

    @property
    def current_sections(self):
        return self._changes
    

    def process(self, image):
        point = image[self.point[1]][self.point[0]]
        value = np.sum(point)
        self._history.append(value)
        self._history = self._history[-self.history_length:]
        if value > self.threshold + self.null_zone:
            if not self._is_high:
                self._is_high = True
                self._color_bgr = self.ENCODER_COLOR_HIGH_BGR
                return True
        elif value <= self.threshold - self.null_zone:
            if self._is_high:
                self._is_high = False
                self._color_bgr = self.ENCODER_COLOR_LOW_BGR
                return True
        else:
            self._color_bgr = self.ENCODER_COLOR_NULL_BGR
        return False

    def overlay_encoder(self, image):
        ep = self.point
        image = cv2.circle(image, ep, 3, self._color_bgr, 1)
        image = cv2.line(image, (ep[0] + 3, ep[1]), (ep[0] + 6, ep[1]), self._color_bgr, 1)
        image = cv2.line(image, (ep[0] - 3, ep[1]), (ep[0] - 6, ep[1]), self._color_bgr, 1)
        image = cv2.line(image, (ep[0], ep[1] + 3), (ep[0], ep[1] + 6), self._color_bgr, 1)
        image = cv2.line(image, (ep[0], ep[1] - 3), (ep[0], ep[1] - 6), self._color_bgr, 1)
        return image

    def overlay_history(self, image):
        for idx in range(len(self._history)):
            height = int((self._history[idx] / (255.0 * 3.0)) * image.shape[0])
            if self._history[idx] > self.threshold + self.null_zone:
                color = self.ENCODER_COLOR_HIGH_BGR
            elif self._history[idx] <= self.threshold - self.null_zone:
                color = self.ENCODER_COLOR_LOW_BGR
            else:
                color = self.ENCODER_COLOR_NULL_BGR
            image = cv2.line(image, (idx, image.shape[0]), (idx, image.shape[0] - height), color, 1)
        theshold_top = image.shape[0] - int(((self.threshold + self.null_zone) / (255.0 * 3.0)) * image.shape[0])
        theshold_bottom = image.shape[0] - int(((self.threshold - self.null_zone) / (255.0 * 3.0)) * image.shape[0])
        image = cv2.line(image, (0, theshold_top), (self.history_length, theshold_top), self.THRESHOLD_MARKER_COLOR, 3)
        image = cv2.line(image, (0, theshold_bottom), (self.history_length, theshold_bottom), self.THRESHOLD_MARKER_COLOR, 3)
        return image
