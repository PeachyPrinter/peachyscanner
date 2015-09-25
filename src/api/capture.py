import numpy as np
import cv2
import cv
import threading
import os
import logging

logger = logging.getLogger('peachy')


class Capture(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        logger.info("Creating Window")
        self.is_running = True
        self.show = 'r'
        self.focus = 120
        self.canny_low = 50
        self.canny_high = 100
        cv.NamedWindow('frame', flags=cv.CV_WINDOW_NORMAL)
        cv2.resizeWindow('frame', 960, 540)
        cv2.setMouseCallback('frame', self.clicky)
        self.cap = cv2.VideoCapture(0)
        self.cap.read()
        self.cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 1080.0)
        self.cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1920.0)
        os.system('''uvcdynctrl  --set='Focus, Auto' 0''')
        os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
        self.video_properties = {
            "CV_CAP_PROP_POS_MSEC": cv.CV_CAP_PROP_POS_MSEC,
            "CV_CAP_PROP_POS_FRAMES": cv.CV_CAP_PROP_POS_FRAMES,
            "CV_CAP_PROP_POS_AVI_RATIO": cv.CV_CAP_PROP_POS_AVI_RATIO,
            "CV_CAP_PROP_FRAME_WIDTH": cv.CV_CAP_PROP_FRAME_WIDTH,
            "CV_CAP_PROP_FRAME_HEIGHT": cv.CV_CAP_PROP_FRAME_HEIGHT,
            "CV_CAP_PROP_FPS": cv.CV_CAP_PROP_FPS,
            "CV_CAP_PROP_FOURCC": cv.CV_CAP_PROP_FOURCC,
            "CV_CAP_PROP_FRAME_COUNT": cv.CV_CAP_PROP_FRAME_COUNT,
            "CV_CAP_PROP_FORMAT": cv.CV_CAP_PROP_FORMAT,
            "CV_CAP_PROP_MODE": cv.CV_CAP_PROP_MODE,
            "CV_CAP_PROP_BRIGHTNESS": cv.CV_CAP_PROP_BRIGHTNESS,
            "CV_CAP_PROP_CONTRAST": cv.CV_CAP_PROP_CONTRAST,
            "CV_CAP_PROP_SATURATION": cv.CV_CAP_PROP_SATURATION,
            "CV_CAP_PROP_HUE": cv.CV_CAP_PROP_HUE,
            "CV_CAP_PROP_GAIN": cv.CV_CAP_PROP_GAIN,
            "CV_CAP_PROP_EXPOSURE": cv.CV_CAP_PROP_EXPOSURE,
            "CV_CAP_PROP_CONVERT_RGB": cv.CV_CAP_PROP_CONVERT_RGB,
            # "CV_CAP_PROP_WHITE_BALANCE_U": cv.CV_CAP_PROP_WHITE_BALANCE_U,
            # "CV_CAP_PROP_WHITE_BALANCE_V": cv.CV_CAP_PROP_WHITE_BALANCE_V,
            "CV_CAP_PROP_RECTIFICATION": cv.CV_CAP_PROP_RECTIFICATION,
            # "CV_CAP_PROP_ISO_SPEED": cv.CV_CAP_PROP_ISO_SPEED,
            # "CV_CAP_PROP_BUFFERSIZE ": cv.CV_CAP_PROP_BUFFERSIZE,
        }
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

    def focus_in(self):
        self.focus += 10
        os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
        logger.info('FOCUS: {}'.format(self.focus))

    def focus_out(self):
        self.focus -= 10
        os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
        logger.info('FOCUS: {}'.format(self.focus))

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
            if key == 'w':
                self.focus_in()
            if key == 's':
                self.focus_out()
            if key == 'W':
                self.focus += 1
                os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
                logger.info('FOCUS: {}'.format(self.focus))
            if key == 'S':
                self.focus -= 1
                os.system('''uvcdynctrl  --set='Focus (absolute)' {}'''.format(self.focus))
                logger.info('FOCUS: {}'.format(self.focus))
            if key == 'u':
                self.canny_low += 10
                logger.info('Canny Low: {}'.format(self.canny_low))
            if key == 'j':
                self.canny_low -= 10
                logger.info('Canny Low: {}'.format(self.canny_low))
            if key == 'i':
                self.canny_high += 10
                logger.info('Canny High: {}'.format(self.canny_high))
            if key == 'k':
                self.canny_high -= 10
                logger.info('Canny High: {}'.format(self.canny_high))
            if key in ['c', 'r', 'm']:
                self.show = key
        self.cap.release()
        cv2.destroyAllWindows()