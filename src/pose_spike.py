import numpy as np
import cv2
import threading
import logging

# from camera_control import CameraControl

logger = logging.getLogger('peachy')


class Capture(object):
    def __init__(self):
        logger.info("Creating Window")
        self.is_running = True
        self.cap = cv2.VideoCapture(0)
        ret, self.frame = self.cap.read()
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)



    def clicky(self, event, x, y, flags, param):
        self.mouse_pos = np.int16([x, y])

    def run(self):
        cv2.namedWindow('frame', flags=cv2.WINDOW_NORMAL)
        # cv2.setMouseCallback('frame', self.clicky, 0)
        # cv2.resizeWindow('frame', 960, 540)
        while(self.is_running):
            ret, frame = self.cap.read()

            # self.frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
            cv2.imshow('frame', frame)
            key = chr(cv2.waitKey(1) & 0xFF)
            if key == 'q':
                break
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    c = Capture()
    c.run()