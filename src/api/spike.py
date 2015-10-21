
import numpy as np
import cv2
import threading
from threading import RLock
import logging
import time

logger = logging.getLogger('peachy')

from camera_control import CameraControl

class Camera(CameraControl):
    def __init__(self,):
        super(Camera, self).__init__()
        self._cap = cv2.VideoCapture(0)
        self._frame = self._cap.read()

        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._frame = self._cap.read()[1]

    def read(self, ):
        return self._cap.read()[1]

    def shutdown(self,):
        if self._cap:
            self._cap.release()


class Capture(threading.Thread):
    def __init__(self, camera):
        threading.Thread.__init__(self)
        self.camera = camera
        self.is_running = True
        self._handlers = []

    def run(self):
        while(self.is_running):
            frame = self.camera.read()
            self._handlers[0].handle(frame, self._handlers[1:])
        print("is running %s" % self.is_running)
        self.is_shutdown = True

    def subscribe(self, handler):
        self._handlers.append(handler)


class Display(object):
    def __init__(self,):
        self.is_init = False

    def init(self):
        cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('frame', 1280, 720)
        cv2.moveWindow('frame', 500, 0)
        self.is_init = True

    def handle(self, frame, handler_chain):
        if not self.is_init:
            self.init()
        frame.roi = self.roi
        handler_chain[0].handle(frame, handler_chain[:-1])
        cv2.imshow('frame', frame)
        key = chr(cv2.waitKey(1) & 0xFF)
        if key == 'q':
            self.is_running = False

    def shutdown(self):
        cv2.destroyAllWindows()

class ImageCapture(object):

    def __init__(self, encoder, frame_height):
        self.encoder = encoder
        self.frame_height = frame_height
        self.buffer = np.zeros((self.frame_height, encoder.possible_posisitions, 3))

    def handle(self, frame):
        should_capture, idx = self.encoder.should_capture_frame_at_index(frame)
        if should_capture:
            self.buffer[0:self.frame_height][idx] = frame[0:self.frame_height][self._capture_column]


class SpikeEncoder(object):
    def __init__(self):
        self.pos = 0

    def should_capture_frame_at_index(self):
        self.pos = (self.pos + 1) % 200
        return (True, self.pos)

if __name__ == '__main__':
    encoder = SpikeEncoder()
    camera = Camera()
    c = Capture(camera)
    display = Display()
    c.subscribe(display)
    i = ImageCapture(encoder, 200)
    c.subscribe(i)
    c.start()
    time.sleep(5)
    c.is_running = False
    time.sleep(1)
    camera.shutdown()
    display.shutdown()


    class KivyUI
        self.cv_ui

        def get_capture(self)
            cv_ui.get_capture


    class controller:


