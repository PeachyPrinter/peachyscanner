import logging
import numpy as np

logger = logging.getLogger('peachy')

class Encoder(object):
    def __init__(self, 
                 degrees_per_step=1.0,
                 encoder_point = [0, 0],
                 threshold = 382,
                 null_zone = 382
                 ):
        self.threshold = threshold
        self.null_zone = null_zone
        self.encoder_point = encoder_point
        self._degrees_per_step = degrees_per_step
        self._changes = 0
        self._is_high = False

    @property
    def degrees(self):
        return self._degrees_per_step * self._changes

    def process(self, image):
        encoder_point = image[self.encoder_point[0]][self.encoder_point[1]]
        encoder_value = np.sum(encoder_point)
        if encoder_value > self.threshold + self.null_zone:
            if not self._is_high:
                self._changes += 1
                self._is_high = True
        elif encoder_value <= self.threshold - self.null_zone:
            if self._is_high:
                self._changes += 1
                self._is_high = False
        else:
            pass