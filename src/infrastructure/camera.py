from cv2 import VideoCapture


class Camera(object):
    def read(self):
        return self._video_capture.read()

    def start(self):
        self._video_capture = VideoCapture()

    def stop(self):
        self._video_capture.release()