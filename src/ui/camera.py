import kivy
from kivy.config import Config
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock


kivy.require('1.9.0')

Builder.load_file('ui/camera.kv')


class CameraControl(BoxLayout):
    text = StringProperty()
    min_value = NumericProperty()
    max_value = NumericProperty()
    value = NumericProperty()

    def __init__(self, **kwargs):
        Logger.info("init: {}".format(self.value))
        super(CameraControl, self).__init__(**kwargs)

    def on_value(self, instance, value):
        Logger.info("value: {}".format(value))


class CameraControls(BoxLayout):
    capture = ObjectProperty()

    def __init__(self, **kwargs):
        super(CameraControls, self).__init__(**kwargs)
        Config.adddefaultsection('camera')
        
        Clock.schedule_once(self._post_init)

    def _post_init(self, instance):
        self._bind_controls()
        self._load_saved_settings()


    def _load_saved_settings(self):
        Logger.info("Loading Camera Settings")
        focus = Config.getdefault('camera', 'focus', 128)
        Logger.info("Loaded focus - {}".format(focus))
        self.focus.value = float(focus)
        brightness = Config.getdefault('camera', 'brightness', 128)
        Logger.info("Loaded brightness - {}".format(brightness))
        self.brightness.value = float(brightness)
        contrast = Config.getdefault('camera', 'contrast', 50)
        Logger.info("Loaded contrast - {}".format(contrast))
        self.contrast.value = float(contrast)
        white_balance = Config.getdefault('camera', 'white_balance', 4200)
        Logger.info("Loaded white_balance - {}".format(white_balance))
        self.white_balance.value = float(white_balance)
        sharpness = Config.getdefault('camera', 'sharpness', 50)
        Logger.info("Loaded sharpness - {}".format(sharpness))
        self.sharpness.value = float(sharpness)

    def _bind_controls(self):
        self.focus.bind(value=self.on_focus)
        self.brightness.bind(value=self.on_brightness)
        self.contrast.bind(value=self.on_contrast)
        self.white_balance.bind(value=self.on_white_balance)
        self.sharpness.bind(value=self.on_sharpness)

    def on_focus(self, instance, value):
        Logger.info("Setting focus - {}".format(value))
        Config.set('camera', 'focus', value)
        self.capture.camera.focus = value

    def on_brightness(self, instance, value):
        Logger.info("Setting brightness - {}".format(value))
        Config.set('camera', 'brightness', value)
        self.capture.camera.brightness = value

    def on_contrast(self, instance, value):
        Logger.info("Setting contrast - {}".format(value))
        Config.set('camera', 'contrast', value)
        self.capture.camera.contrast = value

    def on_white_balance(self, instance, value):
        Logger.info("Setting white_balance - {}".format(value))
        Config.set('camera', 'white_balance', value)
        self.capture.camera.white_balance = value

    def on_sharpness(self, instance, value):
        Logger.info("Setting sharpness - {}".format(value))
        Config.set('camera', 'sharpness', value)
        self.capture.camera.sharpness = value

    def save(self):
        Logger.info('Saving camera settings')
        Config.write()


class CameraControlWrapper(Screen):
    def on_pre_leave(self):
        self.camera_controls.save()
