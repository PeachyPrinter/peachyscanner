from cv2 import VideoCapture


class Camera(object):
    def read():
        raise Exception("Not implemented")

    def start(self):
        self._video_capture = VideoCapture()

    def stop(self):
        raise Exception("Not implemented")