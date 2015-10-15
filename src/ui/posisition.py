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

        roi = Config.getdefault('posisition', 'roi', None)
        if roi:
            Logger.info("ROI Loaded - {}".format(roi))
            self.capture.roi = json.loads(roi)

        roi = Config.getdefault('posisition', 'roi', None)
        if roi:
            Logger.info("ROI Loaded - {}".format(roi))
            self.capture.roi = json.loads(roi)

        encoder_threshold = float(Config.getdefault('posisition', 'encoder_threshold', 200))
        self.capture.encoder_threshold = encoder_threshold
        self.encoder_threshold_widget.value = encoder_threshold


        encoder_null_zone = float(Config.getdefault('posisition', 'encoder_null_zone', 50))
        self.capture.encoder_null_zone = encoder_null_zone
        self.encoder_null_zone_widget.value = encoder_null_zone

        encoder_point = Config.getdefault('posisition', 'encoder_point', None)
        if encoder_point:
            Logger.info("Encoder Point Loaded - {}".format(encoder_point))
            self.capture.encoder_point = tuple(json.loads(encoder_point))

    def select_encoder(self):
        self._disable_all()
        self.capture.select_encoder(self._encoder_call_back)

    def _encoder_call_back(self, encoder_pos):
        self._enable_all()
        Logger.info('Found Encoder: {}'.format(encoder_pos))
        Config.set('posisition', 'encoder_point', json.dumps(encoder_pos))

    def select_roi(self):
        self._disable_all()
        self.capture.select_roi(self._roi_call_back)

    def _roi_call_back(self, roi):
        self._enable_all()
        Logger.info('Found ROI (x,y,w,h: {}'.format(roi))
        Config.set('posisition', 'roi', json.dumps(roi))

    def encoder_threshold(self, value):
        self.capture.encoder_threshold = value
        Logger.info('Encoder Threshold Set at : {}'.format(value))
        Config.set('posisition', 'encoder_threshold', value)

    def encoder_null_zone(self, value):
        self.capture.encoder_null_zone = value
        Logger.info('Encoder Null Zone Set at : {}'.format(value))
        Config.set('posisition', 'encoder_null_zone', value)

    def save_settings(self):
        Logger.info('Saving Settings')
        Config.write()

    def _disable_all(self):
        for child in self.children:
            child.disabled = True

    def _enable_all(self):
        for child in self.children:
            child.disabled = False
