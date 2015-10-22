import numpy as np
import cv2
import threading
import logging
import time


logger = logging.getLogger('peachy')

class ScannerAPI(object):
    def __init__(self):
        self.camera = Camera

    def capture_image(self, call_back):

