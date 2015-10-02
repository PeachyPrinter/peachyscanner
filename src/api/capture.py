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

        self._mouse_pos = [0, 0]
        self._drag_start = None
        self._centre = None
        self._roi = None
        self._encoder_point = None
        self._encoder_threshold = 150
        self._encoder_null_zone = 50
        self._degrees = 0

        self._show_crosshair = False
        self._show_mask = False
        # self._cap = None
        self._cap = cv2.VideoCapture(0)
        self._frame = self._cap.read()
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._frame = self._cap.read()
        self.camera = CameraControl()

        self._lower_range = None
        self._upper_range = None

        self._left_click_call_backs = []
        self._centre_callback = None
        self._roi_callback = None
        self._encoder_callback = None

        self._get_drag = False
        self._dragging = False
        self._level = []

    def _clicky(self, event, x, y, flags, param):
        self._mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self._dragging = True
            self._drag_start = self._mouse_pos
            while len(self._left_click_call_backs) > 0:
                self._left_click_call_backs.pop()(self._mouse_pos[0], self._mouse_pos[1])
        if event == cv2.EVENT_LBUTTONUP and self._get_drag:
            self._roi_selected(self._drag_start, self._mouse_pos)
        if event == cv2.EVENT_LBUTTONUP:
            self._dragging = False

        if event == cv2.EVENT_RBUTTONDOWN:
            pass

    def select_roi(self, callback):
        with self._setting_lock:
            self._roi = None
            self._roi_callback = callback
            self._get_drag = True

    def _roi_selected(self, start, stop):
        self._get_drag = False
        self._drag_start = None
        x = min(start[0], stop[0])
        y = min(start[1], stop[1])
        w = abs(start[0] - stop[0])
        h = abs(start[1] - stop[1])
        self._roi = (x, y, w, h)
        if self._roi_callback:
            self._roi_callback(self._roi)

    def select_encoder(self, callback):
        with self._setting_lock:
            self._encoder_callback = callback
            self._left_click_call_backs.append(self._encoder_selected)

    def _encoder_selected(self, x, y):
        self._encoder_point = (x, y)
        self._degrees = 0
        if self._encoder_callback:
            self._encoder_callback((x, y))

    def show_range(self, low_RGB, high_RGB):
            self._lower_range = np.array([min(low_RGB[2], high_RGB[2]) * 255, min(low_RGB[1], high_RGB[1]) * 255, min(low_RGB[0], high_RGB[0]) * 255])
            self._upper_range = np.array([max(low_RGB[2], high_RGB[2]) * 255, max(low_RGB[1], high_RGB[1]) * 255, max(low_RGB[0], high_RGB[0]) * 255])

    def toggle_mask(self, onoff):
        with self._setting_lock:
            self._show_mask = onoff

    def get_centre(self, call_back):
        with self._setting_lock:
            self._show_crosshair = True
            self._centre_callback = call_back
            self._left_click_call_backs.append(self._set_centre)

    def _set_centre(self, x, y):
        logger.info("Center set to {}, {}".format(x, y))
        self._show_crosshair = False
        self._centre = [x, y]
        if self._centre_callback:
            self._centre_callback([x, y])
            self._centre_callback = None

    @property
    def encoder_threshold(self):
        return self._encoder_threshold

    @encoder_threshold.setter
    def encoder_threshold(self, value):
        self._encoder_threshold = value

    @property
    def encoder_null_zone(self):
        return self._encoder_null_zone

    @encoder_null_zone.setter
    def encoder_null_zone(self, value):
        self._encoder_null_zone = value

    def shutdown(self):
        self.is_running = False

    def _draw_cross_hair(self, frame, pos, color=(0, 255, 0), width=2):
        cv2.line(frame, (0, pos[1]), (frame.shape[1], pos[1]), color, width)
        cv2.line(frame, (pos[0], 0), (pos[0], frame.shape[0]), color, width)

    def _draw_bounding_box(self, frame, tl, lr, color=(0, 0, 255), thickness=2):
        cv2.line(frame, (tl[0], tl[1]), (lr[0], tl[1]), color, thickness)
        cv2.line(frame, (lr[0], tl[1]), (lr[0], lr[1]), color, thickness)
        cv2.line(frame, (lr[0], lr[1]), (tl[0], lr[1]), color, thickness)
        cv2.line(frame, (tl[0], lr[1]), (tl[0], tl[1]), color, thickness)

    def _draw_levels(self, frame, levels):
        for idx in range(0, len(levels)):
            level = levels[idx]
            top = frame.shape[0]

            h = int(float(top) * (level / (2.0 * (255 + 255 + 255))))
            if level >= self._encoder_threshold + self._encoder_null_zone:
                color = (0, 255, 0)
            elif level <= self._encoder_threshold - self._encoder_null_zone:
                color = (0, 0, 255)
            else:
                color = (255, 255, 0)
            cv2.line(frame, (idx, top), (idx, top - h), color, 1)

        h_hi = int(float(top) * ((self._encoder_threshold + self._encoder_null_zone) / (2.0 * (255 + 255 + 255))))
        h_low = int(float(top) * ((self._encoder_threshold - self._encoder_null_zone) / (2.0 * (255 + 255 + 255))))
        cv2.line(frame, (0, top - h_hi), (len(levels) + 5, top - h_hi), (255, 255, 255), 2)
        cv2.line(frame, (0, top - h_low), (len(levels) + 5, top - h_low), (255, 255, 255), 2)

    def _process_encoder(self, frame, original):
        self._level.append(sum(original[self._encoder_point[1], self._encoder_point[0]]) + sum(original[self._encoder_point[1], self._encoder_point[0] + 1]))
        self._level = self._level[-100:]

        self._draw_levels(frame, self._level)

        if self._level[-1] >= self._encoder_threshold + self._encoder_null_zone:
            self.on_count += 1
            if self.on_count >= 2:
                enc_color = (0, 200, 0)
            else:
                enc_color = (200, 200, 0)
            if self.on_count == 2:
                self._degrees += 3.6
                if self._degrees >= 360.0:
                    self._degrees -= 360.0
        elif self._level[-1] <= self._encoder_threshold - self._encoder_null_zone:
            self.on_count = 0
            enc_color = (0, 0, 200)
        else:
            enc_color = (200, 200, 0)
            self.on_count = 0

        cv2.circle(frame, self._encoder_point, 10, enc_color, 5)

    def run(self):
        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('frame', self._clicky, 0)
        cv2.resizeWindow('frame', 960, 540)
        fps = []
        start = time.time()
        self.on_count = 0
        self.off_count = 0
        while(self.is_running):
            with self._setting_lock:
                fps.append(1.0 / (time.time() - start))
                fps = fps[-10:]
                start = time.time()
                ret, original = self._cap.read()
                frame = original

                if (self._lower_range is not None) and (self._upper_range is not None):
                    mask = cv2.inRange(original, self._lower_range, self._upper_range)
                    b, g, r = cv2.split(original)
                    b = cv2.subtract(b, mask)
                    g = cv2.add(g, mask)
                    r = cv2.subtract(r, mask)
                    if self._show_mask:
                        frame = cv2.merge((mask, mask, mask))
                    else:
                        frame = cv2.merge((b, g, r))

                if self._get_drag and self._dragging:
                    self._draw_bounding_box(frame, self._drag_start, self._mouse_pos)

                if self._roi:
                    gray = frame / 4
                    roi = frame[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]]
                    gray[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]] = roi
                    frame = gray

                if self._centre:
                    self._draw_cross_hair(frame, self._centre, (255, 255, 255), 1)

                if self._show_crosshair:
                    self._draw_cross_hair(frame, self._mouse_pos)

                if self._encoder_point:
                    self._process_encoder(frame, original)

                self._frame = frame

                cv2.putText(self._frame, "fps: {:.2f}".format(sum(fps) / float(len(fps))), (5, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.putText(self._frame, "Deg: {}".format(self._degrees), (5, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.imshow('frame', self._frame)

                # cv2.imshow('frame', frame)

                # self.show_data()
                key = chr(cv2.waitKey(1) & 0xFF)
                if key == 'q':
                    break

        if self._cap:
            self._cap.release()
        cv2.destroyAllWindows()
