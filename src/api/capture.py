import numpy as np
import cv2
import threading
from threading import RLock
import logging
import time

from camera_control import CameraControl

logger = logging.getLogger('peachy')


class Capture(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self._setting_lock = RLock()
        logger.info("Creating Window")
        self.is_running = True
        self.show = 'r'

        self.mouse_pos = [0, 0]
        self.drag_start = None
        self.centre = None
        self.roi = None
        self.encoder_point = None
        self.degrees = 0

        self.show_crosshair = False
        self.show_mask = False
        # self.cap = None
        self.cap = cv2.VideoCapture(0)
        self.frame = self.cap.read()
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.frame = self.cap.read()
        self.camera = CameraControl()

        self.lower_range = None
        self.upper_range = None

        self._left_click_call_backs = []
        self._centre_callback = None
        self._roi_callback = None
        self._encoder_callback = None

        self.get_drag = False
        self.dragging = False
        self.show_drag = False

    def clicky(self, event, x, y, flags, param):
        self.mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.drag_start = self.mouse_pos
            while len(self._left_click_call_backs) > 0:
                self._left_click_call_backs.pop()(self.mouse_pos[0], self.mouse_pos[1])
        if event == cv2.EVENT_LBUTTONUP and self.get_drag:
            self.roi_selected(self.drag_start, self.mouse_pos)
        if event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

        if event == cv2.EVENT_RBUTTONDOWN:
            pass

    def select_roi(self, callback):
        with self._setting_lock:
            self.roi = None
            self._roi_callback = callback
            self.get_drag = True

    def roi_selected(self, tl, lr):
        self.get_drag = False
        self.drag_start = None
        x, y, h, w = tl[0], lr[1], tl[1] - lr[1], lr[0] - tl[0]
        self.roi = (x, y, w, h)
        if self._roi_callback:
            self._roi_callback((tl, lr))

    def select_encoder(self, callback):
        with self._setting_lock:
            self._encoder_callback = callback
            self._left_click_call_backs.append(self._encoder_selected)

    def _encoder_selected(self, x, y):
        self.encoder_point = (x, y)
        self.degrees = 0
        if self._encoder_callback:
            self._encoder_callback((x, y))

    def show_range(self, low_RGB, high_RGB):
            self.lower_range = np.array([min(low_RGB[2], high_RGB[2]) * 255, min(low_RGB[1], high_RGB[1]) * 255, min(low_RGB[0], high_RGB[0]) * 255])
            self.upper_range = np.array([max(low_RGB[2], high_RGB[2]) * 255, max(low_RGB[1], high_RGB[1]) * 255, max(low_RGB[0], high_RGB[0]) * 255])

    def hide_range(self):
        pass

    def toggle_mask(self, onoff):
        with self._setting_lock:
            self.show_mask = onoff

    def get_centre(self, call_back):
        with self._setting_lock:
            self.show_crosshair = True
            self._centre_callback = call_back
            self._left_click_call_backs.append(self._set_centre)

    def _set_centre(self, x, y):
        logger.info("Center set to {}, {}".format(x, y))
        self.show_crosshair = False
        self.centre = [x, y]
        if self._centre_callback:
            self._centre_callback([x, y])
            self._centre_callback = None

    def shutdown(self):
        self.is_running = False

    def draw_cross_hair(self, frame, pos, color=(0, 255, 0), width=2):
        cv2.line(frame, (0, pos[1]), (frame.shape[1], pos[1]), color, width)
        cv2.line(frame, (pos[0], 0), (pos[0], frame.shape[0]), color, width)

    def draw_bounding_box(self, frame, tl, lr, color=(0, 0, 255), thickness=2):
        cv2.line(frame, (tl[0], tl[1]), (lr[0], tl[1]), color, thickness)
        cv2.line(frame, (lr[0], tl[1]), (lr[0], lr[1]), color, thickness)
        cv2.line(frame, (lr[0], lr[1]), (tl[0], lr[1]), color, thickness)
        cv2.line(frame, (tl[0], lr[1]), (tl[0], tl[1]), color, thickness)

    def run(self):
        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('frame', self.clicky, 0)
        cv2.resizeWindow('frame', 960, 540)
        fps = []
        start = time.time()
        self.on_count = 0
        while(self.is_running):
            with self._setting_lock:
                fps.append(1.0 / (time.time() - start))
                fps = fps[-10:]
                start = time.time()
                ret, original = self.cap.read()
                frame = original

                if (self.lower_range is not None) and (self.upper_range is not None):
                    mask = cv2.inRange(original, self.lower_range, self.upper_range)
                    b, g, r = cv2.split(original)
                    b = cv2.subtract(b, mask)
                    g = cv2.add(g, mask)
                    r = cv2.subtract(r, mask)
                    if self.show_mask:
                        frame = cv2.merge((mask, mask, mask))
                    else:
                        frame = cv2.merge((b, g, r))

                if self.get_drag and self.dragging:
                    self.draw_bounding_box(frame, self.drag_start, self.mouse_pos)

                if self.roi:
                    gray = frame / 4
                    roi = frame[self.roi[1]:self.roi[1] + self.roi[3], self.roi[0]:self.roi[0] + self.roi[2]]
                    gray[self.roi[1]:self.roi[1] + self.roi[3], self.roi[0]:self.roi[0] + self.roi[2]] = roi
                    frame = gray

                if self.centre:
                    self.draw_cross_hair(frame, self.centre, (255, 255, 255), 1)

                if self.show_crosshair:
                    self.draw_cross_hair(frame, self.mouse_pos)

                if self.encoder_point:
                    if ((sum(original[self.encoder_point[1], self.encoder_point[0]]) +
                         sum(original[self.encoder_point[1], self.encoder_point[0] + 1])) < 100):
                        enc_color = (0, 200, 0)
                        self.on_count += 1
                        if self.on_count == 2:
                            self.degrees += 3.6
                            if self.degrees >= 360.0:
                                self.degrees -= 360.0
                    else:
                        enc_color = (0, 0, 200)
                        self.on_count = 0

                    cv2.circle(frame, self.encoder_point, 10, enc_color, 5)

                self.frame = frame

                cv2.putText(self.frame, "fps: {:.2f}".format(sum(fps) / float(len(fps))), (5, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.putText(self.frame, "Deg: {}".format(self.degrees), (5, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.imshow('frame', self.frame)

                # cv2.imshow('frame', frame)

                # self.show_data()
                key = chr(cv2.waitKey(1) & 0xFF)
                if key == 'q':
                    break

        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
