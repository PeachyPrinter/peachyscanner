import cv2
from cv2 import VideoCapture


class Camera(object):
    def read(self):
        (retVal, image) = self._video_capture.read()
        return image

    def start(self):
        self._video_capture = VideoCapture(0)
        self.shape = self.read().shape

    def stop(self):
        self._video_capture.release()
