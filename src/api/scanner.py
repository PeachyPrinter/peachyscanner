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

logger = logging.getLogger('peachy')


class ScannerAPI(object):

    def __init__(self):
        self.camera = Camera()
        self.camera.start()
        self._default_roi = ROI.set_from_points((0, 0), (self.camera.shape[0], self.camera.shape[1]), self.camera.shape)
        self._default_encoder = Encoder((self.camera.shape[0] / 3, self.camera.shape[1] / 2), 382, 100, 20, 200)

        self.encoder = self._default_encoder
        self.roi = self._default_roi
        self.video_processor = VideoProcessor(self.camera, self.encoder, self.roi)

    def set_region_of_interest(self, point1, point2):
        frame_shape = self.camera.shape
        self.roi = ROI.set_from_points(point1, point2, [frame_shape[1], frame_shape[0], 3])
        self.video_processor.roi = self.roi

    def capture_image(self, call_back=None):
        if call_back:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections), call_back)
        else:
            self.video_processor.subscribe(ImageCapture(self.encoder.sections))

    def configure_encoder(self, point, threshold, null_zone, sections):
        self.encoder = Encoder(point, threshold, null_zone, 20, sections)
        self.video_processor.encoder = self.encoder

    def start(self):
        self.video_processor.start()

    def stop(self):
        self.video_processor.stop()
        self.camera.stop()
