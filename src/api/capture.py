import numpy as np
import cv2
import cv
import threading
import logging

from camera_control import CameraControl

logger = logging.getLogger('peachy')


class Capture(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        logger.info("Creating Window")
        self.is_running = True
        self.show = 'r'
        self.canny_low = 50
        self.canny_high = 100
        cv.NamedWindow('frame', flags=cv.CV_WINDOW_NORMAL)
        cv2.resizeWindow('frame', 960, 540)
        cv2.setMouseCallback('frame', self.clicky)
        self.cap = cv2.VideoCapture(0)
        self.cap.read()
        self.cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 1080.0)
        self.cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1920.0)
        self.camera = CameraControl()
        self.lower_range = np.array([50, 50, 180])
        self.upper_range = np.array([255, 255, 255])

    def clicky(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            logger.info("{}".format(str(self.frame[y, x])))
            self.lower_range = self.frame[y, x]
            logger.info("{},{}".format(self.lower_range, self.upper_range))

        if event == cv2.EVENT_RBUTTONDOWN:
            logger.info("{}".format(str(self.frame[y, x])))
            self.upper_range = self.frame[y, x]
            logger.info("{},{}".format(self.lower_range, self.upper_range))

    def show_data(self):
        for (key, value) in self.video_properties.items():
            logger.info("{} = {}".format(key, self.cap.get(value)))

    def shutdown(self):
        self.is_running = False

    def run(self):
        while(self.is_running):
            ret, frame = self.cap.read()

            if self.show == 'r':
                frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
            if self.show == 'm':
                mask = cv2.inRange(frame, self.lower_range, self.upper_range)
                frame = cv2.resize(mask, (0, 0), fx=1, fy=1)
            if self.show == 'c':
                canny = cv2.Canny(frame, self.canny_low, self.canny_high)
                frame = cv2.resize(canny, (0, 0), fx=1, fy=1)

            self.frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
            cv2.imshow('frame', self.frame)
            # self.show_data()
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                break
        self.cap.release()
        cv2.destroyAllWindows()