import numpy as np
import cv2
import threading
from threading import RLock
import logging
import time

from camera_control import CameraControl

from infrastructure.point_converter import PointConverter
from infrastructure.writer import PLYWriter

logger = logging.getLogger('peachy')


class CenterMixIn(object):
    def __init__(self):
        self._center = None
        self._center_callback = None

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center):
        assert(len(center) == 2)
        self._center = center

    def get_center(self, call_back):
        with self._setting_lock:
            self._show_crosshair = True
            self._center_callback = call_back
            self._left_click_call_backs.append(self._set_center)

    def _set_center(self, frame, x, y):
        logger.info("Center set to {}, {}".format(x, y))
        self._show_crosshair = False
        self._center = [x, y]
        if self._center_callback:
            self._center_callback([x, y])
            self._center_callback = None


class ROIMixIn(object):
    def __init__(self):
        self._roi = None
        self._roi_callback = None

    @property
    def roi(self):
        return self._roi

    @roi.setter
    def roi(self, roi):
        self._roi = roi

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


class EncoderMixIn(object):
    def __init__(self):
        self._encoder_point = None
        self._encoder_threshold = 150
        self._encoder_null_zone = 50
        self._encoder_callback = None

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

    @property
    def encoder_point(self):
        return self._encoder_point

    @encoder_point.setter
    def encoder_point(self, value):
        self._encoder_point = value

    def select_encoder(self, callback):
        with self._setting_lock:
            self._encoder_callback = callback
            self._left_click_call_backs.append(self._encoder_selected)

    def _encoder_selected(self, frame, x, y):
        logger.info("Encoder Point Selected - {},{}".format(x, y))
        if frame.shape[0] > x and frame.shape[1] > y:
            logger.info("Encoder Point Accepted")
            self._encoder_point = (x, y)
            self._degrees = 0
            if self._encoder_callback:
                self._encoder_callback((x, y))
        else:
            logger.info("Encoder Point Rejected")
            self._encoder_point = None
            if self._encoder_callback:
                self._encoder_callback(None)

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
            self._off_count = 0
            self._on_count += 1
            if self._on_count >= 2:
                enc_color = (0, 200, 0)
            else:
                enc_color = (200, 200, 0)
            if self._on_count == 2:
                self._degrees += 1.8
                if self._degrees >= 360.0:
                    self._degrees -= 360.0
        elif self._level[-1] <= self._encoder_threshold - self._encoder_null_zone:
            self._on_count = 0
            self._off_count += 1
            if self._off_count >= 2:
                enc_color = (0, 0, 200)
            else:
                enc_color = (200, 200, 0)
            if self._off_count == 2:
                self._degrees += 1.8
                if self._degrees >= 360.0:
                    self._degrees -= 360.0
        else:
            enc_color = (200, 200, 0)
            self._on_count = 0
            self._off_count = 0

        cv2.circle(frame, self._encoder_point, 10, enc_color, 5)

class Capture(threading.Thread, CenterMixIn, ROIMixIn, EncoderMixIn):
    def __init__(self):
        threading.Thread.__init__(self)
        CenterMixIn.__init__(self)
        ROIMixIn.__init__(self)
        EncoderMixIn.__init__(self)

        self._setting_lock = RLock()
        self.is_running = True
        self.is_shutdown = False
        self._mouse_pos = [0, 0]
        self._drag_start = None
        self._degrees = 0
        self._show_crosshair = False
        self._show_mask = False
        # self._cap = None

        self._cap = cv2.VideoCapture(0)
        self._frame = self._cap.read()
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._frame = self._cap.read()[1]
        self._center = (self._frame.shape[1] / 2, 0)
        self.camera = CameraControl()

        self._lower_range = None
        self._upper_range = None
        self._on_count = 0
        self._off_count = 0

        self._left_click_call_backs = []

        self._capturing_callback = None

        self._get_drag = False
        self._dragging = False
        self._level = []

        self._capture_image = None
        self._capturing = False
        self._capture_file = 'ImageMesh'
        self._frames_aquired = 0
        self._last_degrees = 0

        self.point_converter = PointConverter()
        self._points = None
        self._ply_writer = PLYWriter()

    def _clicky(self, event, x, y, flags, param):
        self._mouse_pos = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            self._dragging = True
            self._drag_start = self._mouse_pos
            while len(self._left_click_call_backs) > 0:
                logger.info("Calling back click")
                self._left_click_call_backs.pop()(self._frame, self._mouse_pos[0], self._mouse_pos[1])
        if event == cv2.EVENT_LBUTTONUP and self._get_drag:
            self._roi_selected(self._drag_start, self._mouse_pos)
        if event == cv2.EVENT_LBUTTONUP:
            self._dragging = False
        if event == cv2.EVENT_RBUTTONDOWN:
            pass

    def show_range(self, low_RGB, high_RGB):
        self._lower_range = np.array([int(min(low_RGB[2], high_RGB[2]) * 255), int(min(low_RGB[1], high_RGB[1]) * 255), int(min(low_RGB[0], high_RGB[0]) * 255)])
        self._upper_range = np.array([int(max(low_RGB[2], high_RGB[2]) * 255), int(max(low_RGB[1], high_RGB[1]) * 255), int(max(low_RGB[0], high_RGB[0]) * 255)])

    def toggle_mask(self, onoff):
        with self._setting_lock:
            self._show_mask = onoff

    def start_capture(self, callback):
        logger.info("Capture Requested")
        with self._setting_lock:
            self._capturing_callback = callback
            self._capturing = True

    def shutdown(self):
        self.is_running = False
        while not self.is_shutdown:
            time.sleep(0.1)
        #TODO better this.

    def _draw_cross_hair(self, frame, pos, color=(0, 255, 0), width=2):
        cv2.line(frame, (0, pos[1]), (frame.shape[1], pos[1]), color, width)
        cv2.line(frame, (pos[0], 0), (pos[0], frame.shape[0]), color, width)

    def _draw_bounding_box(self, frame, tl, lr, color=(0, 0, 255), thickness=2):
        cv2.line(frame, (tl[0], tl[1]), (lr[0], tl[1]), color, thickness)
        cv2.line(frame, (lr[0], tl[1]), (lr[0], lr[1]), color, thickness)
        cv2.line(frame, (lr[0], lr[1]), (tl[0], lr[1]), color, thickness)
        cv2.line(frame, (tl[0], lr[1]), (tl[0], tl[1]), color, thickness)

    def _start_capture(self, frame):
        if self._capture_image is None:
            logger.info("Capture Init")
            self._degrees = 0.0
            self._frames_aquired = 0
            self._last_degrees = -90.0
            logger.info("Starting at {}".format(self._degrees))
            self._capture_image = np.empty((200, self._roi[3], 3))
            self._capture_points = np.empty((200, self._roi[3]))
            logger.info("output array: {}".format(self._capture_image.shape))
        else:
            if self._frames_aquired >= 200:
                logger.info("Capture Compelete")
                self._capture_start = None
                file_header = self._capture_file+"-"+str(time.time())
                cv2.imwrite(file_header+".jpg", self._capture_image)
                self._ply_writer.write_polar_points(file_header + ".ply", self._capture_points)
                self._capture_image = None
                self._capturing = False
                self._last_degrees = False
                if self._capturing_callback:
                    self._capturing_callback(self._capture_file)
                return
        if self._last_degrees is not self._degrees:
            roi = frame[self._roi[1]:self._roi[1] + self._roi[3], self._center[0]]
            turns = int(self._degrees / 1.8)
            self._capture_image[self._frames_aquired] = roi
            self._capture_points[self._frames_aquired] = self._points
            logger.info("Aquired Frame: {} at {}".format(self._frames_aquired, turns))
            self._frames_aquired += 1
        self._last_degrees = self._degrees

    def run(self):
        cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow('frame', 1280, 720)
        cv2.moveWindow('frame', 500, 0)

        cv2.setMouseCallback('frame', self._clicky, 0)
        fps = []
        start = time.time()

        while(self.is_running):
            with self._setting_lock:
                fps.append(1.0 / (time.time() - start))
                fps = fps[-10:]
                start = time.time()
                ret, original = self._cap.read()
                frame = original

                if self._capturing:
                    self._start_capture(original)

                if (self._lower_range is not None) and (self._upper_range is not None) and self._roi:
                    roi = original[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]]
                    mask = cv2.inRange(roi, self._lower_range, self._upper_range)
                    mask_center = self.center[0] - self.roi[0]
                    self._points = self.point_converter.get_points(mask, mask_center)
                    b, g, r = cv2.split(roi)
                    b = cv2.subtract(b, mask)
                    g = cv2.add(g, mask)
                    r = cv2.subtract(r, mask)
                    if self._show_mask:
                        frame[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]] = cv2.merge((mask, mask, mask))
                    else:
                        frame[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]] = cv2.merge((b, g, r))

                if self._get_drag and self._dragging:
                    self._draw_bounding_box(frame, self._drag_start, self._mouse_pos)

                if self._roi:
                    gray = frame / 4
                    roi = frame[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]]
                    gray[self._roi[1]:self._roi[1] + self._roi[3], self._roi[0]:self._roi[0] + self._roi[2]] = roi
                    frame = gray

                if self._center:
                    self._draw_cross_hair(frame, self._center, (255, 255, 255), 1)

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
        self.is_shutdown = True
