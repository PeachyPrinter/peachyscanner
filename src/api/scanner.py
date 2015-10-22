import numpy as np
import cv2
import threading
import logging
import time
from infrastructure.roi import ROI
from infrastructure.encoder import Encoder

from camera_control import Camera

logger = logging.getLogger('peachy')


class ScannerAPI(object):
    def __init__(self):
        self.camera = Camera()
        self.encoder = None

    def set_region_of_interest(self, point1, point2):
        frame_shape = self.camera.shape
        self.roi = ROI.set_from_points(point1, point2, [frame_shape[1], frame_shape[0], 3])

    def capture_image(self, call_back=None):
        raise Exception('Well Now That Was Easy')

    def configure_encoder(self, point, threshold, null_zone, sections):
        self.encoder = Encoder(point, threshold, null_zone, 20, sections)