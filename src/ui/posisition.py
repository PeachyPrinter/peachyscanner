import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.graphics import Color, Line

import json


kivy.require('1.9.0')
Builder.load_file('ui/posisition.kv')


class PositionControl(Screen):
    video = ObjectProperty()
    def __init__(self, scanner, video_widget, **kwargs):
        self.scanner = scanner
        self.section = 'peachyscanner.posisition'
        self._selecting_encoder = False
        self._selecting_roi = False
        self.video_widget = video_widget

        self._encoder_segments = 200
        Config.adddefaultsection(self.section)
        self._load_saved_settings()
        super(PositionControl, self).__init__(**kwargs)
        Window.bind(on_motion=self.on_motion)
        Clock.schedule_once(self._post_init)

    def _post_init(self, instance):
        self.encoder_null_zone_widget.value = self._encoder_null_zone
        self.encoder_threshold_widget.value = self._encoder_threshold
        self._configure_encoder()

    def _load_saved_settings(self):
        roi = json.loads((Config.getdefault(self.section, 'roi', "[0.0, 0.0, 1.0, 1.0]")))
        self.scanner.set_region_of_interest_from_rel_points(*roi)
        self._encoder_threshold = int(Config.getdefault(self.section, 'encoder_threshold', 200))
        self._encoder_null_zone = int(Config.getdefault(self.section, 'encoder_null_zone', 50))
        encoder_point = json.loads(Config.getdefault(self.section, 'encoder_point', '[0.5, 0.5]'))
        self._encoder_point = tuple([float(p) for p in encoder_point])
        if self._encoder_point[0] > 1.0 or self._encoder_point[1] > 1.0:
            self._encoder_point[0] == 0.5
            self._encoder_point[1] == 0.5

    def select_encoder(self):
        self._disable_all()
        self._selecting_encoder = True

    def _encoder_selected(self, encoder_pos):
        self._encoder_point = encoder_pos
        Logger.info('Encoder point set at: {}'.format(str(encoder_pos)))
        Config.set(self.section, 'encoder_point', json.dumps(self._encoder_point))
        self._configure_encoder()
        self._selecting_encoder = False
        self._enable_all()

    def _configure_encoder(self):
        self.scanner.configure_encoder(self._encoder_point, self._encoder_threshold, self._encoder_null_zone, self._encoder_segments)

    def select_roi(self):
        self._disable_all()
        self._selecting_roi = True

    def _roi_selected(self, point1, point2, video_size):
        self._selecting_roi = False
        try:
            self.scanner.set_region_of_interest_from_abs_points(point1, point2, video_size)
            Config.set(self.section, 'roi', json.dumps(self.scanner.roi.get_points()))
        except:
            pass
        self._enable_all()


    # def _roi_call_back(self, roi):
    #     self._enable_all()
    #     Logger.info('Found ROI (x,y,w,h: {}'.format(roi))
    #     Config.set(self.section, 'roi', json.dumps(roi))

    def encoder_threshold(self, value):
        self._encoder_threshold = int(value)
        Logger.info('Encoder Threshold Set at : {}'.format(self._encoder_threshold))
        Config.set(self.section, 'encoder_threshold', self._encoder_threshold)
        self._configure_encoder()

    def encoder_null_zone(self, value):
        self._encoder_null_zone = int(value)
        Logger.info('Encoder Null Zone Set at : {}'.format(self._encoder_null_zone))
        Config.set(self.section, 'encoder_null_zone', self._encoder_null_zone)
        self._configure_encoder()

    def save_settings(self):
        Logger.info('Saving Settings')
        Config.write()

    def _disable_all(self):
        for child in self.children:
            child.disabled = True

    def _enable_all(self):
        for child in self.children:
            child.disabled = False

    def on_motion(self, instance, etype, motionevent):
        video_pos = self.video_widget.video_pos
        video_size = self.video_widget.video_size

        if etype == 'begin':
            self.drag_start = None
        if etype == 'end':
            self.drag_end = (motionevent.pos[0], motionevent.pos[1])
            self.video_widget.selection(0, 0, 0, 0)
            if self._selecting_encoder:
                x = motionevent.pos[0] - video_pos[0]
                y = motionevent.pos[1] - video_pos[1]
                if (x >= 0 and x < video_size[0]) and (y >= 0 and y < video_size[1]):
                    self._encoder_selected((x / video_size[0], 1.0 - (y / video_size[1])))
            if self._selecting_roi:
                x1 = self.drag_start[0] - video_pos[0]
                y1 = video_size[1] - self.drag_start[1] - video_pos[1]
                x2 = motionevent.pos[0] - video_pos[0]
                y2 = video_size[1] - motionevent.pos[1] - video_pos[1]
                self._roi_selected((x1, y1), (x2, y2), video_size)

        if etype == 'update' and self._selecting_roi:
            if self.drag_start is None:
                self.drag_start = (motionevent.pos[0], motionevent.pos[1])
            self.drag_current = (motionevent.pos[0], motionevent.pos[1])
            size = (self.drag_current[0] - self.drag_start[0], self.drag_current[1] - self.drag_start[1])
            self.video_widget.selection(self.drag_start[0], self.drag_start[1], size[0], size[1])

