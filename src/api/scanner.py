import numpy as np
import cv2
import threading
import logging
import time
from infrastructure.roi import ROI
from infrastructure.encoder import Encoder

from infrastructure.camera import Camera
from infrastructure.video_processor import VideoProcessor
from infrastructure.data_capture import ImageCapture
from infrastructure.laser_detector import LaserDetector


logger = logging.getLogger('peachy')


class ScannerAPI(object):

    def __init__(self):
        self.camera = Camera()
        self.camera.start()
        self._default_roi = ROI(0.0, 0.0, 1.0, 1.0)
        self._default_encoder = Encoder((0.2, 0.2), 382, 100, 20, 200)

        self.encoder = self._default_encoder
        self.roi = self._default_roi
        self._laser_detector = LaserDetector.from_rgb_float((0.8, 0.0, 0.0), (1.0, 0.2, 0.2))
        self.video_processor = VideoProcessor(self.camera, self.encoder, self.roi, self.laser_detector)

    def set_region_of_interest_from_abs_points(self, point1, point2, frame_shape_xy):
        self.roi = ROI.set_from_abs_points(point1, point2, [frame_shape_xy[1], frame_shape_xy[0], 3])
        self.video_processor.roi = self.roi

    def set_region_of_interest_from_rel_points(self, x_rel, y_rel, w_rel, h_rel):
        self.roi = ROI(x_rel, y_rel, w_rel, h_rel)
        self.video_processor.roi = self.roi

    def capture_image(self, call_back=None):
        if call_back:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections), call_back)
        else:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections))

    def get_feed_image(self, size):
        return self.video_processor.get_bounded_image(*size)

    def configure_encoder(self, point, threshold, null_zone, sections):
        self.encoder = Encoder(point, threshold, null_zone, 20, sections)
        self.video_processor.encoder = self.encoder

    def start(self):
        self.video_processor.start()

    def stop(self):
        self.video_processor.stop()
        self.camera.stop()
