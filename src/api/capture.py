import numpy as np
import cv2
import threading
from threading import RLock
import logging
import time

from camera_control import CameraControl

from infrastructure.point_converter import PointConverter
from infrastructure.writer import PLYWriter
from infrastructure.encoder import Encoder
from infrastructure.roi import ROI

logger = logging.getLogger('peachy')

class CaptureAPI(object):
    def __init__(self):
        self.ENCODER_SECTIONS = 200
        self.encoder = Encoder(
                 sections= self.ENCODER_SECTIONS,
                 point = (0, 0),
                 threshold = 382,
                 null_zone = 382,
                 history_length = 30)
        self._roi = ROI()

        self._roi_callback = None
        self._encoder_callback = None

    @property
    def roi(self):
        return [self._roi.x, self._roi.y, self._roi.w, self._roi.h]

    @roi.setter
    def roi(self, value):
        self._roi.set(*value)

    @property
    def encoder_threshold(self):
        return self.encoder.threshold

    @encoder_threshold.setter
    def encoder_threshold(self, value):
        self.encoder.threshold = value

    @property
    def encoder_null_zone(self):
        return self.encoder.null_zone

    @encoder_null_zone.setter
    def encoder_null_zone(self, value):
        self.encoder.null_zone = value

    @property
    def encoder_point(self):
        return self.encoder.point

    @encoder_point.setter
    def encoder_point(self, value):
        self.encoder.point = value


    def select_encoder(self, callback):
        with self._setting_lock:
            self._encoder_callback = callback
            self._left_click_call_backs.append(self._encoder_selected)

    def _encoder_selected(self, frame, x, y):
        logger.info("Encoder Point Selected - {},{}".format(x, y))
        if frame.shape[0] > x and frame.shape[1] > y:
            logger.info("Encoder Point Accepted")
            self.encoder.point = (x, y)
            if self._encoder_callback:
                self._encoder_callback((x, y))
        else:
            logger.info("Encoder Point Rejected")
            if self._encoder_callback:
                self._encoder_callback(None)

    def select_roi(self, callback):
        with self._setting_lock:
            self._roi_callback = callback
            self._get_drag = True

    def _roi_selected(self, start, stop):
        self._get_drag = False
        self._drag_start = None
        self._roi.set_from_points(start,stop)
        if self._roi_callback:
            self._roi_callback(self.roi)

class Capture(threading.Thread, CaptureAPI):
    def __init__(self, status):
        threading.Thread.__init__(self)
        CaptureAPI.__init__(self)
        self._status = status
        self._ply_writer = PLYWriter()

        self._setting_lock = RLock()
        self.is_running = True
        self.is_shutdown = False
        self._mouse_pos = [0, 0]
        self._drag_start = None
        self._show_mask = False

        self._cap = cv2.VideoCapture(0)
        self._frame = self._cap.read()
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._frame = self._cap.read()[1]
        self._center = self._frame.shape[1] / 2
        self.camera = CameraControl()

        self._lower_range = None
        self._upper_range = None

        self._left_click_call_backs = []

        self._capturing_callback = None

        self._get_drag = False
        self._dragging = False

        self._capture_image = None
        self._capturing = False
        self._capture_file = 'ImageMesh'
        self._frames_aquired = 0
        self._last_degrees = 0

        self.point_converter = PointConverter()
        self._points = None
        

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

    def _draw_center_line(self, frame, color=(255, 255, 255), width=1):
        cv2.line(frame, (self._center,0), (self._center,frame.shape[0]), color, width)
        return frame

    def show_range(self, low_RGB, high_RGB):
        self._lower_range = np.array([int(min(low_RGB[2], high_RGB[2]) * 255), int(min(low_RGB[1], high_RGB[1]) * 255), int(min(low_RGB[0], high_RGB[0]) * 255)])
        self._upper_range = np.array([int(max(low_RGB[2], high_RGB[2]) * 255), int(max(low_RGB[1], high_RGB[1]) * 255), int(max(low_RGB[0], high_RGB[0]) * 255)])

    def _draw_bounding_box(self, frame, tl, lr, color=(0, 0, 255), thickness=2):
        cv2.line(frame, (tl[0], tl[1]), (lr[0], tl[1]), color, thickness)
        cv2.line(frame, (lr[0], tl[1]), (lr[0], lr[1]), color, thickness)
        cv2.line(frame, (lr[0], lr[1]), (tl[0], lr[1]), color, thickness)
        cv2.line(frame, (tl[0], lr[1]), (tl[0], tl[1]), color, thickness)

    def _start_capture(self, frame):
        if self._capture_image is None:
            logger.info("Capture Init")
            self._status.operation = "Capturing Points"
            self._status.progress = 0.0
            self._last_degrees = self.encoder.degrees - 90.0
            self._frames_aquired = 0
            logger.info("Starting at {}".format(self.encoder.degrees))
            self._capture_image = np.empty((self.ENCODER_SECTIONS, self._roi.h, 3))
            self._capture_points = np.zeros((self.ENCODER_SECTIONS, self._roi.h))
            logger.info("output array: {}".format(self._capture_image.shape))
            self._status.points = self._capture_points
        else:
            if self._frames_aquired >= self.ENCODER_SECTIONS:
                logger.info("Capture Compelete")
                self._status.points = self._capture_points
                self._status.operation = "Capture Complete"
                self._capture_start = None
                file_header = self._capture_file+"."+str(time.time())
                cv2.imwrite(file_header+".jpg", self._capture_image)
                with open(file_header + ".ply", 'w') as outfile:
                    self._ply_writer.write_polar_points(outfile, self._capture_points)
                self._capture_image = None
                self._capturing = False
                self._last_degrees = False
                if self._capturing_callback:
                    self._capturing_callback(self._capture_file)
                return
        if self._last_degrees != self.encoder.degrees:
            roi = frame[self._roi.y:self._roi.y + self._roi.h, self._center]
            self._capture_image[self._frames_aquired] = roi
            self._capture_points[self._frames_aquired] = self._points
            logger.info("Aquired Frame: {}".format(self._frames_aquired))
            self._status.progress = self._frames_aquired / float(self.ENCODER_SECTIONS)
            self._status.points = self._capture_points
            self._frames_aquired += 1
            self._last_degrees = self.encoder.degrees

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

                self.encoder.process(original)

                if self._capturing:
                    self._start_capture(original)

                if (self._lower_range is not None) and (self._upper_range is not None) and self._roi.x:
                    roi = self._roi.get(original)
                    mask = cv2.inRange(roi, self._lower_range, self._upper_range)
                    mask_center = self._center - self._roi.x
                    self._points = self.point_converter.get_points(mask, mask_center)
                    b, g, r = cv2.split(roi)
                    b = cv2.subtract(b, mask)
                    g = cv2.add(g, mask)
                    r = cv2.subtract(r, mask)
                    if self._show_mask:
                        self._roi.replace(frame, cv2.merge((mask, mask, mask)))
                    else:
                        self._roi.replace(frame, cv2.merge((b, g, r)))

                if self._get_drag and self._dragging:
                    self._draw_bounding_box(frame, self._drag_start, self._mouse_pos)

                frame = self._roi.overlay(frame)
                frame = self._draw_center_line(frame)
                frame = self.encoder.overlay_encoder(frame)
                frame = self.encoder.overlay_history(frame)

                self._frame = frame

                cv2.putText(self._frame, "fps: {:.2f}".format(sum(fps) / float(len(fps))), (5, 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.putText(self._frame, "Deg: {}".format(self.encoder.degrees), (5, 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                cv2.imshow('frame', self._frame)

                key = chr(cv2.waitKey(1) & 0xFF)
                if key == 'q':
                    break

        if self._cap:
            self._cap.release()
        cv2.destroyAllWindows()
        self.is_shutdown = True
