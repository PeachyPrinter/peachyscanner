import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.core.window import Window

import json


kivy.require('1.9.0')
Builder.load_file('ui/posisition.kv')


class PositionControl(Screen):
    def __init__(self, scanner, **kwargs):
        super(PositionControl, self).__init__(**kwargs)
        Config.adddefaultsection('posisition')
        Window.bind(on_motion=self.on_motion)
        # Clock.schedule_once(self._post_init)
        self.scanner = scanner
        self._encoder_point = (0, 0)
        self._selecting_encoder = True

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
        self._selecting_encoder = True

    def _encoder_selected(self, encoder_pos):
        self._encoder_point = encoder_pos
        Logger.info('Encoder point set at: {}'.format(str(encoder_pos)))
        self._configure_encoder()
        self._selecting_encoder = False
        self._enable_all()

    def _configure_encoder(self):
        self.scanner.configure_encoder(self._encoder_point, 500, 100, 100)

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

    def on_motion(self, instance, etype, motionevent):
        if etype == 'end':
            if self._selecting_encoder:
                video_pos = App.get_running_app().video_pos
                video_size = App.get_running_app().video_size
                x = motionevent.pos[0] - video_pos[0]
                y = motionevent.pos[1] - video_pos[1]
                if (x >= 0 and x < video_size[0]) and (y >= 0 and y < video_size[1]):
                    self._encoder_selected((x / video_size[0], 1.0 - (y / video_size[1])))
                else:
                    pass