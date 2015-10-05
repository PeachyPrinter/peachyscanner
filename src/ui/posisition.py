import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty


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
        pass

    def select_centre(self):
        self._disable_all()
        self.capture.get_centre(self._points_cb)

    def _points_cb(self, pos):
        self._enable_all()
        Logger.info('Found centre: {}'.format(pos))

    def select_encoder(self):
        self._disable_all()
        self.capture.select_encoder(self._encoder_cb)

    def _encoder_cb(self, encoder_pos):
        self._enable_all()
        Logger.info('Found Encoder: {}'.format(encoder_pos))

    def select_roi(self):
        self._disable_all()
        self.capture.select_roi(self._roi_cb)

    def _roi_cb(self, roi):
        self._enable_all()
        Logger.info('Found ROI (x,y,w,h: {}'.format(roi))

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