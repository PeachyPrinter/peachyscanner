import logging
import numpy as np
import cv2

logger = logging.getLogger('peachy')

class Encoder(object):
    _history = []
    def __init__(self,
                 point=(0, 0),
                 threshold=382,
                 null_zone=382,
                 history_length=20,
                 sections=1
                 ):
        self.threshold = threshold
        self.null_zone = null_zone
        self.ENCODER_COLOR_LOW_BGR =  (0,   0,   255)
        self.ENCODER_COLOR_HIGH_BGR = (0,   255, 0  )
        self.ENCODER_COLOR_NULL_BGR = (0,   255, 255)
        self.THRESHOLD_MARKER_COLOR = (255, 255, 255)

        self.history_length = history_length

        self._color_bgr = self.ENCODER_COLOR_LOW_BGR
        self._is_high = False
        # self._history = []
        self.position = 0
        self.sections = sections
        self.relitive_point_xy = point

    @property
    def current_sections(self):
        return self._changes

    def should_capture_frame_for_section(self, image):
        if self.process(image):
            self.position = (self.position + 1) % self.sections
            return (True, self.position)
        else:
            return (False, self.position)

    def process(self, image):
        absolute_point_xy = (int(image.shape[1] * self.relitive_point_xy[0]), int(image.shape[0] * self.relitive_point_xy[1]))
        point = image[absolute_point_xy[1], absolute_point_xy[0]]
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
        mask = np.zeros(image.shape, dtype='uint8')
        ep = (int(self.relitive_point_xy[0] * image.shape[1]), int(self.relitive_point_xy[1] * image.shape[0]))
        mask = cv2.circle(mask, ep, 3, self._color_bgr, 1)
        mask = cv2.line(mask, (ep[0] + 3, ep[1]), (ep[0] + 6, ep[1]), self._color_bgr, 1)
        mask = cv2.line(mask, (ep[0] - 3, ep[1]), (ep[0] - 6, ep[1]), self._color_bgr, 1)
        mask = cv2.line(mask, (ep[0], ep[1] + 3), (ep[0], ep[1] + 6), self._color_bgr, 1)
        mask = cv2.line(mask, (ep[0], ep[1] - 3), (ep[0], ep[1] - 6), self._color_bgr, 1)
        return mask

    def overlay_history(self, image):
        history = list(self._history[-self.history_length:])
        mask = np.zeros(image.shape, dtype='uint8')
        for idx in range(len(history)):
            height = int((history[idx] / (255.0 * 3.0)) * mask.shape[0])
            if history[idx] > self.threshold + self.null_zone:
                color = self.ENCODER_COLOR_HIGH_BGR
            elif history[idx] <= self.threshold - self.null_zone:
                color = self.ENCODER_COLOR_LOW_BGR
            else:
                color = self.ENCODER_COLOR_NULL_BGR
            mask = cv2.line(mask, (idx, mask.shape[0]), (idx, mask.shape[0] - height), color, 1)
        theshold_top = mask.shape[0] - int(((self.threshold + self.null_zone) / (255.0 * 3.0)) * mask.shape[0])
        theshold_bottom = mask.shape[0] - int(((self.threshold - self.null_zone) / (255.0 * 3.0)) * mask.shape[0])
        mask = cv2.line(mask, (0, theshold_top), (self.history_length, theshold_top), self.THRESHOLD_MARKER_COLOR, 3)
        mask = cv2.line(mask, (0, theshold_bottom), (self.history_length, theshold_bottom), self.THRESHOLD_MARKER_COLOR, 3)
        return mask
