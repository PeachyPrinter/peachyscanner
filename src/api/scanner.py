import numpy as np
import cv2
import threading
import logging
import time
from infrastructure.roi import ROI
from infrastructure.encoder import Encoder

from infrastructure.camera import Camera
from infrastructure.video_processor import VideoProcessor
from infrastructure.data_capture import ImageCapture, PointCapture
from infrastructure.laser_detector import LaserDetector, LaserDetector2


logger = logging.getLogger('peachy')


class ScannerAPI(object):

    def __init__(self):
        self.camera = Camera()
        self.camera.start()
        self._default_roi = ROI(0.0, 0.0, 1.0, 1.0)
        self._default_encoder = Encoder((0.2, 0.2), 382, 100, 20, 200)
        self._default_laser_detector = LaserDetector2(225, (3, 3), 'red')

        self.encoder = self._default_encoder
        self.roi = self._default_roi
        self.laser_detector = self._default_laser_detector
        self.video_processor = VideoProcessor(self.camera, self.encoder, self.roi, self.laser_detector)

    def set_region_of_interest_from_abs_points(self, point1, point2, frame_shape_xy):
        self.roi = ROI.set_from_abs_points(point1, point2, [frame_shape_xy[1], frame_shape_xy[0], 3])
        self.video_processor.roi = self.roi

    def set_region_of_interest_from_rel_points(self, x_rel, y_rel, w_rel, h_rel):
        self.roi = ROI(x_rel, y_rel, w_rel, h_rel)
        self.video_processor.roi = self.roi

    def capture_image(self, call_back=None, section_offset = 0):
        if call_back:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections, section_offset), call_back)
        else:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections, section_offset))

    def capture_points(self, call_back=None):
        if call_back:
            self.video_processor.subscribe(PointCapture(self.encoder.sections), call_back)
        else:
            self.video_processor.subscribe(PointCapture(self.encoder.sections))

    def get_feed_image(self, size):
        return self.video_processor.get_bounded_image(*size)

    def configure_encoder(self, point, threshold, null_zone, sections):
        self.encoder = Encoder(point, threshold, null_zone, 20, sections)
        self.video_processor.encoder = self.encoder

    def configure_laser_detector(self, low_rbg_float, high_rgb_float):
        self.laser_detector = LaserDetector.from_rgb_float(low_rbg_float, high_rgb_float)
        self.video_processor.laser_detector = self.laser_detector

    def configure_laser_detector2(self, threshold, filter_size_yx, color):
        self.laser_detector = LaserDetector2(threshold, filter_size_yx, color)
        self.video_processor.laser_detector = self.laser_detector

    def start(self):
        self.video_processor.start()

    def stop(self):
        self.video_processor.stop()
        self.camera.stop()
