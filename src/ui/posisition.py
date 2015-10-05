import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty

import json


kivy.require('1.9.0')
Builder.load_file('ui/posisition.kv')


class PositionControl(Screen):
    capture = ObjectProperty()

    def __init__(self, **kwargs):
        super(PositionControl, self).__init__(**kwargs)
        Config.adddefaultsection('posisition')
        Clock.schedule_once(self._post_init)

    def _post_init(self, instance):
        self._load_saved_settings()

    def _load_saved_settings(self):
        center = Config.getdefault('posisition', 'center', None)
        if center:
            Logger.info("Center Loaded - {}".format(center))
            self.capture.center = json.loads(center)

        roi = Config.getdefault('posisition', 'roi', None)
        if roi:
            Logger.info("ROI Loaded - {}".format(roi))
            self.capture.roi = json.loads(roi)

    def select_center(self):
        self._disable_all()
        self.capture.get_center(self._center_call_back)

    def _center_call_back(self, center):
        self._enable_all()
        Logger.info('Found Center: {}'.format(center))
        Config.set('posisition', 'center', json.dumps(center))
        Config.write()

    def select_encoder(self):
        self._disable_all()
        self.capture.select_encoder(self._encoder_cb)

    def _encoder_cb(self, encoder_pos):
        self._enable_all()
        Logger.info('Found Encoder: {}'.format(encoder_pos))

    def select_roi(self):
        self._disable_all()
        self.capture.select_roi(self._roi_call_back)

    def _roi_call_back(self, roi):
        self._enable_all()
        Logger.info('Found ROI (x,y,w,h: {}'.format(roi))
        Config.set('posisition', 'roi', json.dumps(roi))
        Config.write()

    def encoder_threshold(self, value):
        self.capture.encoder_threshold = value
        Logger.info('Encoder Set at : {}'.format(value))

    def encoder_null_zone(self, value):
        App.get_running_app().capture.encoder_null_zone = value
        Logger.info('Encoder Null Zone Set at : {}'.format(value))

    def _disable_all(self):
        for child in self.children:
            child.disabled = True

    def _enable_all(self):
        for child in self.children:
            child.disabled = False